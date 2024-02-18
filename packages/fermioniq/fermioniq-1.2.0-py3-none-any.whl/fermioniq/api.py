import json
import urllib.parse
from datetime import datetime
from typing import Any

import requests
from pydantic import BaseModel
from requests import Response

# DOCUMENT THIS


class ApiError(RuntimeError):

    status_code: int
    reason: str
    url: str
    response_body: str

    def __init__(
        self,
        msg: Any,
        status_code: int,
        reason: str,
        url: str,
        body: str,
    ):
        super().__init__(msg)
        self.status_code = status_code
        self.reason = reason
        self.response_body = body
        self.url = url


class NoiseModel(BaseModel):
    description: str
    name: str


class JwtResponse(BaseModel):
    jwt_token: str
    user_id: str
    expiration_date: datetime


class WebsocketResponse(BaseModel):
    url: str


class JobResponse(BaseModel):
    id: str
    user_id: str
    creation_time: str
    status: str
    payload_digest: str
    status_code: int


class CancelJobResponse(BaseModel):
    cancelled: bool


class DeleteJobResponse(BaseModel):
    job_id: str
    deleted: bool


class RemoteConfig(BaseModel):
    id: str
    name: str
    description: str
    default: bool


class SasUrlResponse(BaseModel):
    sas_url: str
    expiry_date: str


class Api:

    _base_url: str
    _api_key: str | None

    def __init__(self, base_url: str, api_key: str | None) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def _raise_for_status(self, response: requests.Response) -> None:
        http_error_msg: str | None = None
        text = response.text
        if 400 <= response.status_code < 500:
            http_error_msg = (
                f"{response.status_code} Client "
                f"Error: {response.reason} for url: "
                f"{response.url}. Message: {text}"
            )

        elif 500 <= response.status_code < 600:
            http_error_msg = (
                f"{response.status_code} Server "
                f"Error: {response.reason} for url: "
                f"{response.url}. Message: {text}"
            )

        if http_error_msg:
            raise ApiError(
                http_error_msg,
                status_code=response.status_code,
                reason=response.reason,
                url=response.url,
                body=text,
            )

    def _get_default_headers(self, token: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["x-functions-key"] = self._api_key
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def schedule_job(self, token: str, payload: dict[str, Any]) -> JobResponse:
        url: str = urllib.parse.urljoin(self._base_url, "api/jobs")
        headers: dict[str, str] = self._get_default_headers(token=token)
        headers["Content-Type"] = "application/json"

        r: Response = requests.post(url, headers=headers, data=json.dumps(payload))
        self._raise_for_status(response=r)
        return JobResponse.parse_obj(r.json())

    def get_job_by_id(self, token: str, job_id: str) -> JobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return JobResponse.parse_obj(r.json())

    def cancel_job(self, token: str, job_id: str) -> CancelJobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/cancel")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.post(url, headers=headers)
        self._raise_for_status(response=r)
        return CancelJobResponse.parse_obj(r.json())

    def delete_job(self, token: str, job_id: str) -> DeleteJobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.delete(url, headers=headers)
        self._raise_for_status(response=r)
        return DeleteJobResponse.parse_obj(r.json())

    def get_job_results(self, token: str, job_id: str) -> dict[str, Any]:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/results")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return r.json()

    def get_all_jobs(
        self, token: str, offset: int = 0, limit: int = 10
    ) -> list[JobResponse]:
        url: str = urllib.parse.urljoin(
            self._base_url, f"api/jobs?offset={offset}&limit={limit}"
        )
        headers: dict[str, str] = self._get_default_headers(token=token)
        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [JobResponse.parse_obj(o) for o in r.json()]

    def get_noise_models(self, token: str) -> list[NoiseModel]:
        url: str = urllib.parse.urljoin(self._base_url, "api/noise-models")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [NoiseModel.parse_obj(o) for o in r.json()]

    def get_token(
        self,
        access_token_id: str,
        access_token_secret: str,
    ) -> JwtResponse:
        url: str = urllib.parse.urljoin(self._base_url, "api/login")
        headers: dict[str, str] = self._get_default_headers()
        headers["Content-Type"] = "application/json"

        payload: dict[str, str] = {
            "access_token_id": access_token_id,
            "access_token_secret": access_token_secret,
        }
        r: Response = requests.post(url, headers=headers, data=json.dumps(payload))
        self._raise_for_status(response=r)
        return JwtResponse.parse_obj(r.json())

    def get_websocket_connection(
        self,
        token: str,
        group: str,
    ) -> WebsocketResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/websockets/{group}")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)

        return WebsocketResponse.parse_obj(r.json())

    def get_remote_configs(self, token: str) -> list[RemoteConfig]:
        url: str = urllib.parse.urljoin(self._base_url, "api/remote-configs")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [RemoteConfig.parse_obj(o) for o in r.json()]

    def get_job_data_sas_url(self, token: str, job_id: str) -> SasUrlResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/jobdata")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return SasUrlResponse.parse_obj(r.json())
