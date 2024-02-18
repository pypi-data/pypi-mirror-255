import asyncio
import os
import sys
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

import websockets.exceptions
from pydantic import BaseModel

from fermioniq.api import (
    Api,
    ApiError,
    CancelJobResponse,
    DeleteJobResponse,
    JobResponse,
    NoiseModel,
    RemoteConfig,
    SasUrlResponse,
)
from fermioniq.custom_logging.printing import Printer, StringMessage
from fermioniq.emulator_job import EmulatorJob, JobResult
from fermioniq.emulator_message import EmulatorMessage
from fermioniq.websocket_handler import WebsocketHandler, WebsocketMessage


class NoResultsErrorReason(Enum):
    JOB_FAILED = 1
    JOB_NOT_FINISHED = 2


class NoResultsError(RuntimeError):
    def __init__(
        self,
        msg: Any,
        reason: NoResultsErrorReason,
    ):
        super().__init__(msg)
        self.reason = reason


class ClientConfig(BaseModel):
    """
    The ClientConfig class contains configuration options for the Fermioniq
    class.

    Attributes
    -----------
    access_token_id
        API Key. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_ID
    access_token_secret
        API Secret. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_SECRET
    ws_event_loop
        The event loop to be used by the Fermioniq class.
        If set to None, a new event loop will be created. Users can provide their own event loop if desired.
    verbosity_level
        Level of Client verbosity. The higher the number, the more emulator output will
        be sent to the client. This has an impact on runtime performance and costs.

    Examples
    --------
    >>> custom_event_loop = asyncio.new_event_loop()
    >>> config = ClientConfig(ws_event_loop=custom_event_loop)
    >>> fermioniq = Client(config=config)
    """

    ws_event_loop: asyncio.AbstractEventLoop | None = None
    access_token_id: str | None = None
    access_token_secret: str | None = None
    verbosity_level: int = 0

    class Config:
        arbitrary_types_allowed = True


class Client:
    """
    The client class provides an interface to interact with the Fermioniq API.
    It allows users to schedule, manage,
    and retrieve the results of EmulatorJobs. Additionally, it provides
    websocket functionality for subscribing to job events and receiving updates
    in real-time. The class handles token management, ensuring that a valid
    token is always used when interacting with the API.

    Examples
    --------

    >>> fermioniq = Client()

    >>> # Schedule a new job
    >>> job = EmulatorJob(circuit="some_circuit_definition")
    >>> job_response = fermioniq.schedule_async(job)

    >>> # Retrieve a specific job
    >>> job_response = fermioniq.job(job_id="some_job_id")

    >>> # Retrieve all jobs
    >>> jobs_list = fermioniq.jobs()

    >>> # Subscribe to job events
    >>> fermioniq.subscribe_to_events(job_id="some_job_id", on_msg_callback=my_callback)
    """

    _config: ClientConfig
    _token: str | None = None
    _token_exp: datetime | None = None
    _keep_ws_open: bool = False
    _api_base_url: str
    _api_key: str | None
    _websocket_handler: WebsocketHandler
    _loop: AbstractEventLoop
    _access_token_secret: str
    _access_token_id: str

    def __init__(
        self,
        access_token_id: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        verbosity_level: int = 0,
        ws_event_loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """ """
        self._config = ClientConfig(
            access_token_id=access_token_id,
            access_token_secret=access_token_secret,
            verbosity_level=verbosity_level,
            ws_event_loop=ws_event_loop,
        )

        if self._config.verbosity_level < 0:
            self._config.verbosity_level = 0
        elif self._config.verbosity_level > 2:
            self._config.verbosity_level = 2

        access_token_id = os.getenv(
            "FERMIONIQ_ACCESS_TOKEN_ID", self._config.access_token_id
        )
        if not access_token_id:
            raise RuntimeError(
                (
                    "Missing ACCESS_TOKEN_ID. Please provide "
                    "via FermioniqConfig or environment variable"
                )
            )

        access_token_secret = os.getenv(
            "FERMIONIQ_ACCESS_TOKEN_SECRET", self._config.access_token_secret
        )
        if not access_token_secret:
            raise RuntimeError(
                (
                    "Missing ACCESS_TOKEN_SECRET. Please provide via "
                    "FermioniqConfig or environment variable"
                )
            )

        self._access_token_secret = access_token_secret
        self._access_token_id = access_token_id

        self._api_base_url = os.getenv(
            "FERMIONIQ_API_BASE_URL",
            "https://fermioniq-api-fapp-prod.azurewebsites.net",
        )
        self._api_key = os.getenv(
            "FERMIONIQ_API_KEY",
            "gCUVmJOKVCdPKRYpgk7nNWM_kTAsZfPeYTbte2sNuKtXAzFuYdj9ag==",
        )

        self._api = Api(self._api_base_url, api_key=self._api_key)

        self._loop = (
            asyncio.get_event_loop()
            if not self._config.ws_event_loop
            else self._config.ws_event_loop
        )
        self._websocket_handler = WebsocketHandler(loop=self._loop)

    def noise_models(self) -> list[NoiseModel]:
        """
        Retrieve all available noise models.

        Returns
        -------
        noise_models
            A list of NoiseModel objects
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_noise_models(token=self._token)

    def get_results(self, job_id: str) -> JobResult:
        """
        Retrieve the job results if available.

        Parameters
        ----------
        job_id
            The ID of the job to retrieve the results for.

        Returns
        -------
        job_result
            A JobResult object containing the results of the job.

        Raises
        ------
        NoResultsError
            When results are not available
        ApiError
            When job can't be found or authorization fails
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        try:
            results = self._api.get_job_results(self._token, job_id)
            return JobResult(
                status_code=0,
                job_outputs=results["emulator_output"],
                job_metadata=results["metadata"],
            )
        except ApiError:
            # dont do anything. we handle it below
            pass

        # ApiError indicates that we don't have the results available.
        # It could be because the job is still running or it has finished
        # with error. Retrieve job and do a check on status
        job = self.job(job_id)
        if job.status == "finished":
            raise NoResultsError(
                (
                    f"Error retrieving results for job: {job_id}. The "
                    "job finished with error."
                ),
                reason=NoResultsErrorReason.JOB_FAILED,
            )
        else:
            raise NoResultsError(
                (
                    f"Error retrieving results for job: {job_id}. The "
                    f"status is '{job.status}'. Try again later."
                ),
                reason=NoResultsErrorReason.JOB_NOT_FINISHED,
            )

    def job(self, job_id: str) -> JobResponse:
        """
        Retrieve the job with the specified job_id.

        Parameters
        ----------
        job_id
            The ID of the job to retrieve.

        Returns
        ------
        job
            A JobResponse object containing the job details.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_job_by_id(self._token, job_id)

    def get_status(self, job_id: str) -> str:
        """
        Retrieve the status of the job with id job_id.

        Parameters
        ----------
        job_id
            The ID of the job to check the status of.

        Returns
        -------
        status
            Status of the job (as a string).
        """
        job = self.job(job_id)
        return job.status

    def remote_configs(self) -> list[RemoteConfig]:
        """
        Retrieve all remote configurations.

        Returns
        -------
        remote_configs
            A list of RemoteConfig objects that are available to use.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        return self._api.get_remote_configs(self._token)

    def jobs(self, offset: int = 0, limit: int = 10) -> list[JobResponse]:
        """
        Retrieve all jobs.

        Returns
        -------
        jobs
            A list of JobResponse objects containing the details of all jobs.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        return self._api.get_all_jobs(self._token, offset=offset, limit=limit)

    def get_job_data_download_url(self, job_id: str) -> SasUrlResponse:
        """
        Returns a download url for retrieving the job data package. The link is
        valid for 1 hour, then it must be retrieved again

        Returns
        -------
        download_url
            A SasUrlResponse object containing the download link
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_job_data_sas_url(self._token, job_id)

    def delete(self, job_id: str) -> DeleteJobResponse:
        """
        Deletes job given by id.

        Returns
        -------
        response
            A DeleteJobResponse object
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.delete_job(self._token, job_id)

    def cancel(self, job_id: str) -> CancelJobResponse:
        """
        Cancels a job

        Parameters
        ----------
        job_id
            The ID of the job to cancel.

        Returns
        -------
        response
            A CancelJobResponse object
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.cancel_job(self._token, job_id=job_id)

    def schedule_and_wait(
        self,
        job: EmulatorJob,
        logger: Callable[[str], None] | None = None,
        cancel_on_interrupt: bool = True,
    ) -> JobResult:
        """
        Schedule a new job and wait for it to finish.

        Parameters
        ----------
        job
            The EmulatorJob to be scheduled.
        logger
            An optional callback function for logging messages, set to
            python's print for unprocessed messages.
        cancel_on_interrupt
            If True, the job will be cancelled on Keyboard interrupt signal

        Returns
        -------
        job_result
            A JobResult object containing the results of the job.
        """
        if logger is None:
            logger = Printer().pprint

        logger(str(StringMessage("Submitting job.")))

        new_job: JobResponse = self.schedule_async(job)

        logger(str(StringMessage(f"Job scheduled. Id: '{new_job.id}'")))

        def logger_callback(message: EmulatorMessage) -> None:
            # nonlocal status_code
            if logger and message.event_type == "LOG":
                logger(message.job_output)

        self.subscribe_to_events(
            job_id=new_job.id,
            on_msg_callback=logger_callback,
            cancel_on_interrupt=cancel_on_interrupt,
        )

        if logger is not None:  # For mypy
            logger(str(StringMessage("Retrieving results")))
        return self.get_results(new_job.id)

    def _get_remote_config_id(self, job: EmulatorJob) -> str:
        remote_configs = self.remote_configs()
        if job.remote_config_name:
            remote_config = [
                rc for rc in remote_configs if rc.name == job.remote_config_name
            ]
            if not remote_config:
                available_configs = [rc.name for rc in remote_configs]
                raise RuntimeError(
                    (
                        f"Remote config with name {job.remote_config_name} "
                        f"does not exist. Use one of: {available_configs}"
                    )
                )

            return remote_config[0].id

        default_config = [rc for rc in remote_configs if rc.default]
        if not default_config:
            available_configs = [rc.name for rc in remote_configs]
            raise RuntimeError(
                (
                    f"No config provided and no default config found. Use "
                    f"one of {available_configs}."
                )
            )
        return default_config[0].id

    def schedule_async(self, job: EmulatorJob) -> JobResponse:
        """
        Schedule a new job asynchronously.

        Parameters
        ----------
        job
            The EmulatorJob to be scheduled.

        Returns
        -------
        job_response
            A JobResponse object containing the details of the scheduled job.
        """

        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        remote_config_id = self._get_remote_config_id(job)

        payload: dict[str, Any] = {
            "circuit": job.circuit,
            "config": job.config,
            "noise_model": job.noise_model,
            "verbosity_level": self._config.verbosity_level,
            "remote_config_id": remote_config_id,
        }

        remote_job = self._api.schedule_job(self._token, payload)
        job_id = remote_job.id

        job.job_id = job_id

        return remote_job

    def unsubscribe(self):
        self._keep_ws_open = False
        if self._websocket_handler.is_connected():
            asyncio.get_running_loop().create_task(
                self._websocket_handler.close(),
            )

    def subscribe_to_events(
        self,
        job_id: str,
        on_msg_callback: Callable[[EmulatorMessage], None] | None = None,
        return_as_task: bool = False,
        cancel_on_interrupt: bool = False,
        log_updates: bool = False,
        logger: Callable[[str], None] | None = None,
    ) -> None | asyncio.Task[None]:
        """
        Subscribe to job events and execute a callback function when a
        new message is received.

        Parameters
        ----------
        job_id
            The ID of the job to subscribe to.
        on_msg_callback
            A callback function to be executed when a new message is received.
        return_as_task
            If True, returns the task instead of executing it immediately.
        cancel_on_interrupt
            If True, and return_as_task is False, the job will be cancelled on
            Keyboard interrupt signal
        log_updates
            If True, live updates will be printed via ``logger``, or a default
            logger if ``logger`` is not set.
        logger
            Logger to use for live updates (if set).

        Returns
        -------
        task
            None if return_as_task is False, otherwise an asyncio.Task object.
        """
        if log_updates and not logger:
            logger = Printer().pprint

        # First check if the job has already finished
        if self.job(job_id).status == "finished":
            return None

        def on_message(msg: WebsocketMessage):
            if on_msg_callback:
                on_msg_callback(msg.data)
            else:
                if logger and msg.data.event_type == "LOG":
                    logger(msg.data.job_output)
            if msg.data.event_type == "FINISHED":
                if self._websocket_handler.is_connected():
                    asyncio.get_running_loop().create_task(
                        self._websocket_handler.close()
                    )
                    self._keep_ws_open = False

        if return_as_task:
            task: asyncio.Task[None] = self._loop.create_task(
                self._websocket_event_loop(
                    group=job_id,
                    on_message_callback=on_message,
                )
            )
            return task

        try:
            # block until _websocket_event_loop is closed
            self._loop.run_until_complete(
                self._websocket_event_loop(
                    group=job_id,
                    on_message_callback=on_message,
                )
            )
            return None
        except KeyboardInterrupt:
            self._keep_ws_open = False
            if cancel_on_interrupt:
                self.cancel(job_id=job_id)
            raise

    def _ensure_valid_token(self) -> None:
        """
        Ensure the access token is valid. If the token is invalid or expired,
        it will try to refresh it.
        """
        if self._token is None or self._token_expired():
            token_response = self._api.get_token(
                self._access_token_id, self._access_token_secret
            )
            self._token_exp = token_response.expiration_date
            self._token = token_response.jwt_token

    def _token_expired(self) -> bool:
        """
        Check if the access token is expired.

        Returns
        -------
        expired
            True if the token is expired, False otherwise.
        """
        if self._token is None or self._token_exp is None:
            return True
        expired_offset = timedelta(days=0, seconds=1)
        return self._token_exp - datetime.now(tz=timezone.utc) < expired_offset

    def _websocket_reconnect(self, group: str) -> str | None:
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        try:
            ws_response = self._api.get_websocket_connection(
                token=self._token, group=group
            )
            return ws_response.url
        except Exception as err:
            print(f"Websocket reconnect error: {err}", file=sys.stderr)
            return None

    async def _websocket_event_loop(
        self,
        group: str,
        on_message_callback: Callable[[WebsocketMessage], None],
    ):
        """
        Asynchronous loop for handling websocket messages. Calls the
        on_message_callback when a new message is received.

        Parameters
        ----------
        group
            The group to subscribe to.
        on_message_callback
            A callback function to be executed when a new message is received.
        """
        url: str | None = None

        url = self._websocket_reconnect(group=group)
        if not url:
            raise RuntimeError("Error getting websocket connection string")

        self._keep_ws_open = True
        while self._keep_ws_open:
            try:
                if not self._websocket_handler.is_connected():
                    if url is None:
                        raise ValueError("url is None")
                    # auto reconnect. also reget token
                    await self._websocket_handler.connect(url=url)

                    joined = await self._websocket_handler.join_group(
                        group=group,
                    )
                    if not joined:
                        raise RuntimeError(f"Error joining group: {group}")

                # joined now get data

                await self._websocket_handler.get_messages(
                    on_message=on_message_callback,
                )
            except websockets.exceptions.InvalidStatusCode as err:
                # there was some error connecting. lets try again when
                # status code is 401 UNAUTHORIZED. maybe something
                # was temporarily wrong on the backend
                await self._websocket_handler.close(
                    close_actual_connection=False,
                )
                await asyncio.sleep(1)
                if err.status_code == 401:
                    url = self._websocket_reconnect(group=group)
                    if not url:
                        self._keep_ws_open = False
                else:
                    self._keep_ws_open = False
                    print(f"Websocket error: {err}: ", file=sys.stderr)

            except websockets.exceptions.ConnectionClosed:
                # backend closed connection on us.
                await self._websocket_handler.close(
                    close_actual_connection=False,
                )

            except websockets.exceptions.WebSocketException as err:
                await self._websocket_handler.close(
                    close_actual_connection=False,
                )
                print(f"Websocket error {err}: ", file=sys.stderr)
