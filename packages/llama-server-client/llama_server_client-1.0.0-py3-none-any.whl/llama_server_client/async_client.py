from typing import Optional
from zmq import asyncio as zmq_asyncio
import zmq

from llama_server_client.base_client import BaseLlamaClient
from llama_server_client.schema import HealthCheck
from llama_server_client.schema.base import Base, T
from llama_server_client.schema.completion import ChatCompletionRequest, ChatCompletion
from llama_server_client.schema.zmq_message_header import (
    ZmqMessageType, create_message_header, ZmqMessageHeader, ZmqMessageStatus
)
from llama_server_client.schema.session_state import SessionStateRequest, SessionState
from llama_server_client.error import LlamaClientError


class AsyncLlamaClient(BaseLlamaClient):
    """
    AsyncLlamaClient is an asynchronous client class for communication with a server using ZeroMQ with asyncio.
    It handles socket creation, sending requests, and receiving responses with an option for timeouts.
    """

    def _create_context(self):
        return zmq_asyncio.Context()

    def _create_socket(self):
        return self.context.socket(zmq.REQ)

    async def _send_request(self, zmq_message_type: ZmqMessageType, request: Optional[T] = None) -> Optional[T]:
        """
        Asynchronously sends a request to the server, and waits for a response, handling timeouts.

        :param zmq_message_type: The type of the ZeroMQ message to be sent.
        :param request: The request object to be sent, if applicable.
        :return: The unpacked response if successful, or raises a timeout exception.
        """
        message_header = create_message_header(zmq_message_type)

        message_parts = [message_header.msgpack_pack()]
        if request:
            message_parts.append(request.msgpack_pack())

        await self.socket.send_multipart(message_parts)

        try:
            resp_messages = await self.socket.recv_multipart()
            if len(resp_messages) > 2:
                raise ValueError("Invalid response length")

            response_header = ZmqMessageHeader.msgpack_unpack(resp_messages[0])
            if response_header.status == ZmqMessageStatus.ERROR:
                raise LlamaClientError(response_header)

            response_body: Base = zmq_message_type.get_associated_class
            return response_body.msgpack_unpack(resp_messages[1])
        except zmq.Again:
            self._initialize_context_and_socket()
            raise TimeoutError(f"Request timed out after {self.timeout} milliseconds")

    async def send_chat_completion_request(self, request: ChatCompletionRequest) -> Optional[ChatCompletion]:
        """
        Asynchronously sends a ChatCompletionRequest to the server and waits for a ChatCompletion response.

        :param request: The ChatCompletionRequest to send.
        :return: A ChatCompletion response or None if timed out.
        """
        return await self._send_request(ZmqMessageType.CHAT_COMPLETION, request)

    async def send_session_state_request(self, request: SessionStateRequest) -> Optional[SessionState]:
        """
        Asynchronously sends a SessionStateRequest to the server and waits for a SessionState response.

        :param request: The SessionStateRequest to send.
        :return: A SessionState response or None if timed out.
        """
        return await self._send_request(ZmqMessageType.SESSION_STATE, request)

    async def send_health_check_request(self) -> Optional[HealthCheck]:
        """
        Asynchronously sends a HealthCheck request to the server and waits for a HealthCheck response.

        :return: A HealthCheck response or None if timed out.
        """
        return await self._send_request(ZmqMessageType.HEALTH_CHECK)
