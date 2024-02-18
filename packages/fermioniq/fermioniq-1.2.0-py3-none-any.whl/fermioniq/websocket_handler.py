import asyncio
import json
import sys
from concurrent.futures import TimeoutError
from typing import Callable

import websockets.legacy.client
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError
from websockets.client import WebSocketClientProtocol
from websockets.typing import Subprotocol

from fermioniq.emulator_message import EmulatorMessage

# DOCUMENT THIS


class WebsocketMessage(BaseModel):
    message_type: str = Field(alias="type")
    from_user_id: str | None = Field(alias="fromUserId")
    group: str
    data_type: str = Field(alias="dataType")
    data: EmulatorMessage


class WebsocketHandler:
    _ws: WebSocketClientProtocol | None
    _loop: asyncio.AbstractEventLoop | None
    _ws_recv_timeout_threshold: int = 60

    def __init__(self, loop: asyncio.AbstractEventLoop | None = None):
        self._ws = None
        self._loop = loop

    def is_connected(self):
        return self._ws

    async def close(self, close_actual_connection: bool = True):
        if self._ws and close_actual_connection:
            try:
                await self._ws.close()
            except:
                pass
        self._ws = None

    async def join_group(self, group: str) -> bool:
        if not self._ws:
            raise ValueError("WebsocketHandler not connected yet")

        data = json.dumps({"type": "joinGroup", "group": group})
        await self._ws.send(data)
        response_data = await self._ws.recv()
        response = json.loads(response_data)

        if "event" in response and response["event"] == "connected":
            return True

        return False

    async def connect(self, url: str):
        """
        Establish a websocket connection and join the specified group.

        Parameters
        ----------

        url:
            The websocket url
        """

        if self._ws:
            return

        self._ws = await websockets.legacy.client.Connect(
            url,
            subprotocols=[Subprotocol("json.webpubsub.azure.v1")],
            loop=self._loop,
        )

    async def get_messages(self, on_message: Callable[[WebsocketMessage], None]):
        assert self._loop is not None
        if not self._ws:
            raise ValueError("Websocket not connected")

        # counts how often we havent received a message from websocket
        timeout_count = 0

        # flag that indicates whether we have a websocket timeout.
        websocket_timeout = False

        # flag that indicates whether we count the timeouts
        # this will only be set once we have received at least one message.
        # otherwise it will fire even when a job is in the queue and waiting
        # to be processed
        timeout_count_active = False

        while not websocket_timeout and self._ws is not None:
            try:
                raw_data = await asyncio.wait_for(self._ws.recv(), timeout=1)
            except asyncio.exceptions.TimeoutError:
                if timeout_count_active:
                    # print(f'timeout: {timeout_count}', file=sys.stderr)
                    timeout_count += 1
                    if timeout_count > self._ws_recv_timeout_threshold:
                        websocket_timeout = True

                continue

            timeout_count = 0
            timeout_count_active = True

            try:
                payload = json.loads(raw_data)

                message = WebsocketMessage.parse_obj(payload)

                if message.data.event_type == "PING":
                    # ignore ping
                    continue

                # if message.data.event_type == "FINISHED":
                #    print('emulator finished message')

                on_message(message)

            except ValidationError as e:
                print(
                    f"Pydantic validation error: {e} - {e.raw_errors}", file=sys.stderr
                )
            except json.decoder.JSONDecodeError as e:
                print(
                    f"Got message. But had error decoding JSON: ",
                    e,
                    "payload: ",
                    raw_data,
                    file=sys.stderr,
                )

        if websocket_timeout:
            raise RuntimeError("Websocket timeout")
