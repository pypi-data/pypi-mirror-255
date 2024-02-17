from abc import ABC, abstractmethod
from typing import Optional

import zmq

from llama_server_client.schema.base import T
from llama_server_client.schema.zmq_message_header import ZmqMessageType


class BaseLlamaClient(ABC):
    """
    BaseLlamaClient is an abstract base class for LlamaClient and AsyncLlamaClient.
    It contains the common functionalities shared between both synchronous and asynchronous clients.
    """

    def __init__(self, host: str, timeout: int = 360000):
        self.host = host
        self.timeout = timeout
        self.context = None
        self.socket = None
        self._initialize_context_and_socket()

    def _initialize_context_and_socket(self):
        """
        Initializes the ZeroMQ context and creates a socket with the current timeout setting.
        Calls the abstract methods _create_context and _create_socket for specific implementations.
        """
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

        self.context = self._create_context()
        self.socket = self._create_socket()
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect(self.host)

    def close(self):
        """
        Closes the socket and terminates the ZeroMQ context.
        """
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

    def __del__(self):
        """
        Destructor to ensure resources are freed when the instance is destroyed.
        """
        self.close()

    @abstractmethod
    def _create_context(self):
        """
        Abstract method to create the ZeroMQ context.
        Needs to be implemented in derived classes.
        """
        pass

    @abstractmethod
    def _create_socket(self):
        """
        Abstract method to create the ZeroMQ socket.
        Needs to be implemented in derived classes.
        """
        pass

    @abstractmethod
    def _send_request(self, zmq_message_type: ZmqMessageType, request: Optional[T] = None) -> Optional[T]:
        """
        Abstract method to send a request to the server.
        This method needs to be implemented in derived classes.
        """
        pass
