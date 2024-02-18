import json
import time
import asyncio
import websockets

from urllib import parse
from asyncio import CancelledError
from websockets.connection import State
from typing import Any, AsyncGenerator, Callable
from websockets.legacy.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from pulsar_sdk_py.constants import DEFAULT_TIMEOUT
from pulsar_sdk_py.websocket.encryption import encrypt_message
from pulsar_sdk_py.sleep import wait_for_condition, ConditionFailed
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.exceptions import APIError, SerializationError, WrongResponseFormat
from pulsar_sdk_py.websocket.websocket_types import BalancesMessage, TimeseriesMessage
from pulsar_sdk_py.dataclasses.schemas import Timeseries, WalletIntegrations, WalletNFTs, WalletTokens


NO_MORE_MESSAGES_IN_WEBSOCKET = "stream_end"
WEBSOCKET_ABORTED_MESSAGE = "websocket_aborted"
WEBSOCKET_ABORTED_ERROR_MESSAGE = "WebSocket connection was closed and all ongoing messages were aborted."


class MessageFuture:
    def __init__(self):
        self.future = asyncio.Future()

    async def get(self) -> Any:
        return await self.future

    def set_result(self, result: Any):
        self.future.set_result(result)

    def set_exception(self, exception: Exception):
        self.future.set_exception(exception)


class WebSocketClient:
    api_key: str
    base_url: str
    callback_handler: dict[str, Callable] = {}
    message_futures: dict[str, list[MessageFuture]] = {}
    web_socket_is_opening: bool = False
    web_socket_is_closing: bool = False
    websocket_conn: WebSocketClientProtocol | None
    handle_websocket_loop_task: asyncio.Task | None = None

    def __init__(self, api_key: str, ws_url: str) -> None:
        self.base_url = ws_url
        self.api_key = api_key
        self.websocket_conn = None

    async def transition_to_open(self) -> None:
        while True:
            if self.websocket_conn and self.websocket_conn.state == State.OPEN:
                return
            if not self.web_socket_is_opening:
                break
            await self.wait_for_websocket_opening_completion()
        self.web_socket_is_opening = True
        try:
            if not self.websocket_conn:
                await self.create_new_websocket_connection()
                return
            match self.websocket_conn.state:
                case State.CONNECTING:
                    # Wait for the connection to open
                    await self.wait_for_state(State.OPEN)
                case State.CLOSING:
                    # Wait for it to close
                    await self.wait_for_state(State.CLOSED)
                case State.CLOSED:
                    # Establish a new connection
                    await self.create_new_websocket_connection()
        finally:
            self.web_socket_is_opening = False

    async def transition_to_closed(self) -> None:
        if self.web_socket_is_closing:
            await self.wait_for_websocket_closing_completion()
        self.web_socket_is_closing = True
        try:
            # If there are pending messages or callbacks, or no websocket connection, don't close the connection
            if len(self.message_futures) != 0 or len(self.callback_handler) != 0 or not self.websocket_conn:
                return

            match self.websocket_conn.state:
                case State.OPEN | State.CONNECTING:
                    # If the connection is still opening, wait for it to open
                    if self.websocket_conn.state == State.CONNECTING:
                        await self.wait_for_state(State.OPEN)
                    # If there are pending messages or callbacks, don't close the connection
                    if len(self.message_futures) != 0 or len(self.callback_handler) != 0:
                        return
                    await self.websocket_conn.close()
                    self.handle_websocket_loop_task.cancel()
                    await self.wait_for_state(State.CLOSED)
                case State.CLOSING:
                    # Wait for closure to complete
                    await self.wait_for_state(State.CLOSED)
        finally:
            self.web_socket_is_closing = False

    async def create_new_websocket_connection(self, attempt: int = 1) -> None:
        if attempt > 3:
            raise APIError("Failed to connect to WebSocket after multiple attempts", status_code=500)

        dict_to_send = json.dumps({"api_key": self.api_key, "timestamp": time.time()})
        access_token = encrypt_message(dict_to_send)
        url_with_api_key = f"{self.base_url}?access_token={parse.quote_plus(access_token)}"
        self.websocket_conn = await websockets.connect(url_with_api_key)

        try:
            await wait_for_condition(
                condition_check=lambda: self.websocket_conn and self.websocket_conn.state == State.OPEN,
                timeout=5,
                raise_on_condition=lambda: self.websocket_conn
                and self.websocket_conn.state in [State.CLOSING, State.CLOSED],
            )
        except ConditionFailed:
            try:
                await self.websocket_conn.recv()
            except ConnectionClosedError as exc:
                if not self.websocket_conn.closed:
                    await self.websocket_conn.close()
                raise APIError(exc.reason) from exc
        except asyncio.TimeoutError as exc:
            await self.websocket_conn.close()
            if attempt >= 3:
                raise APIError("WebSocket connection timeout", status_code=408) from exc
            await self.create_new_websocket_connection(attempt + 1)

        # Not sure if necessary, just in case the task gets garbage collected
        self.handle_websocket_loop_task = asyncio.create_task(self.handle_websocket_loop())

    async def handle_websocket_loop(self) -> None:
        try:
            while True:
                data = await self.websocket_conn.recv()
                message = json.loads(data)
                request_id = message["event"]["request_id"]
                if callback := self.callback_handler.get(request_id):
                    callback(message)
        except ConnectionClosedError as exc:
            await self.handle_websocket_error(exc)
        except (CancelledError, ConnectionClosedOK) as exc:
            await self.handle_websocket_closure()
        except Exception as exc:
            await self.handle_websocket_error(exc)

    async def handle_websocket_closure(self) -> None:
        for futures in self.message_futures.values():
            for future in futures:
                if future.future.done():
                    continue
                future.set_result(WEBSOCKET_ABORTED_MESSAGE)

    async def handle_websocket_error(self, exc: ConnectionClosedError | Exception) -> None:
        for request_id, futures in self.message_futures.items():
            for future in futures:
                if future.future.done():
                    continue
                if isinstance(exc, ConnectionClosedError):
                    future.set_exception(
                        APIError(f"WebSocket connection closed unexpectedly: {exc.reason}", status_code=exc.code)
                    )
                else:
                    future.set_exception(
                        APIError(f"Unexpected error occurred while handling WebSocket: {exc}", status_code=500)
                    )
            self.cleanup_request(request_id)

    async def send_message(self, message: BalancesMessage | TimeseriesMessage) -> Any:
        await self.transition_to_open()
        if not self.websocket_conn or self.websocket_conn.state != State.OPEN:
            raise APIError("Failed to send message: WebSocket connection is not open", status_code=503)
        await self.websocket_conn.send(json.dumps(message))

    async def handle_response(
        self,
        request_id: str,
        msg: BalancesMessage | TimeseriesMessage,
        finished_event_type: str,
    ):
        if self.web_socket_is_closing:
            await self.wait_for_websocket_closing_completion()
        self.setup_callback_handler(request_id, finished_event_type)
        try:
            async for message in self.send_message_and_process_messages(request_id, msg):
                yield message
        finally:
            self.perform_final_cleanup(request_id)

    def setup_callback_handler(self, request_id: str, finished_event_type: str) -> None:
        message_future = MessageFuture()
        self.message_futures[request_id] = [message_future]

        def callback_handler(message: dict) -> None:
            event_dict = self.get_event_dict(message)
            current_message_future = self.message_futures[request_id][-1]
            if error_message := event_dict.get("error_message"):
                current_message_future.set_exception(APIError(error_message, status_code=500))
                return
            if event_dict.get("is_error"):
                current_message_future.set_exception(
                    APIError("An error occurred while processing the request", status_code=500)
                )
                return
            event_type: str = event_dict["key"]
            event_payload = event_dict["payload"]
            if event_type == finished_event_type:
                current_message_future.set_result(NO_MORE_MESSAGES_IN_WEBSOCKET)
                return
            if "PREFETCH" in event_type or "FINISHED" in event_type:
                return
            self.message_futures[request_id].append(MessageFuture())
            item = self.process_payload(event_payload["type"], event_payload["data"])
            current_message_future.set_result(item)

        self.callback_handler[request_id] = callback_handler

    async def send_message_and_process_messages(
        self, request_id: str, msg: BalancesMessage | TimeseriesMessage
    ) -> AsyncGenerator[Any, None]:
        await self.send_message(msg)
        while True:
            message = await self.wait_for_message(request_id)
            if message is NO_MORE_MESSAGES_IN_WEBSOCKET:
                break
            if message is WEBSOCKET_ABORTED_MESSAGE:
                raise APIError(WEBSOCKET_ABORTED_ERROR_MESSAGE, status_code=503)
            yield message

    async def wait_for_message(self, request_id: str) -> Any:
        message_future = self.message_futures[request_id][0]
        try:
            message = await asyncio.wait_for(message_future.get(), timeout=DEFAULT_TIMEOUT)
            self.message_futures[request_id].pop(0)
            return message
        except asyncio.TimeoutError as exc:
            raise APIError("WebSocket response timeout.", status_code=408) from exc
        except APIError as exc:
            raise exc

    @staticmethod
    def process_payload(
        payload_type: str, payload_data: dict
    ) -> Timeseries | WalletIntegrations | WalletNFTs | WalletTokens:
        """
        Process the payload data in a WebSocket response.

        This method processes the payload data in a WebSocket response, converting it to a more easily usable
        format.

        Args:
            payload_type (str): The type of the payload data in the response.
            payload_data (dict): The payload data to process.

        Yields:
            Any: The processed payload data from the response.

        Raises:
            SerializationError: If an error occurs during serialization of the payload data.

        """
        try:
            if payload_type.startswith("Timeseries"):
                return serialize_to_dataclass(payload_data[0], Timeseries)
            elif payload_type.startswith("AggregateWalletIntegrations"):
                return serialize_to_dataclass(payload_data, WalletIntegrations)
            elif payload_type.startswith("NFTItem"):
                return serialize_to_dataclass(payload_data, WalletNFTs)
            elif payload_type.startswith("AggregateWalletTokens"):
                return serialize_to_dataclass(payload_data, WalletTokens)
        except Exception as exc:
            # Handle serialization error
            raise SerializationError(
                f"An error occurred during serialization: {exc}\nSerializing {payload_type}."
            ) from exc
        raise SerializationError(f"No serializer found for payload type {payload_type}")

    @staticmethod
    def get_event_dict(response: dict) -> dict:
        """
        A coroutine that returns the event dictionary from the WebSocket server response.

        This method is responsible for parsing the response from the WebSocket server and returning the event
        dictionary contained within.

        Args:
            request_id (str): The ID of the request being made.
            response (str): The response received from the WebSocket server.

        Returns:
            The event dictionary contained within the WebSocket server response.

        Raises:
            WrongResponseFormat: If the response from the WebSocket server is not in the expected format.

        """
        event_dict = response.get("event")
        if not event_dict:
            raise WrongResponseFormat("Response does not contain 'event' dictionary.")
        if "request_id" not in event_dict:
            raise WrongResponseFormat("Response 'event' dictionary does not contain 'request_id' key.")
        return event_dict

    def perform_final_cleanup(self, request_id: str) -> None:
        self.cleanup_request(request_id)
        if len(self.message_futures) == 0 and len(self.callback_handler) == 0:

            async def delayed_transition_to_closed():
                await asyncio.sleep(1)  # Wait for 1 second
                await self.transition_to_closed()

            asyncio.create_task(delayed_transition_to_closed())

    def cleanup_request(self, request_id: str) -> None:
        if request_id in self.callback_handler:
            del self.callback_handler[request_id]
        if request_id in self.message_futures:
            del self.message_futures[request_id]

    async def wait_for_state(self, desired_state: State) -> None:
        await wait_for_condition(lambda: self.websocket_conn and self.websocket_conn.state == desired_state, 10)

    async def wait_for_websocket_closing_completion(self) -> None:
        await wait_for_condition(lambda: not self.web_socket_is_closing, 10)

    async def wait_for_websocket_opening_completion(self) -> None:
        await wait_for_condition(lambda: not self.web_socket_is_opening, 10)
