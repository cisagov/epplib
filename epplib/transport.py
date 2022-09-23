#
# Copyright (C) 2021-2022  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.
#
"""A transport layer to support the EPP client."""
import logging
import socket
import ssl
from abc import ABC, abstractmethod
from os import PathLike
from typing import Optional, Union

from epplib.exceptions import TransportError

PathType = Union[str, PathLike]

_LOGGER = logging.getLogger(__name__)


class Transport(ABC):
    """Abstract base class for Transport."""

    @abstractmethod
    def connect(self) -> None:
        """Open the connection to the EPP server."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection gracefully."""

    @abstractmethod
    def send(self, message: bytes) -> None:
        """Send data to the server.

        Args:
            message: The message to be sent to the server.

        Raises:
            TransportError: When an error occurs while sending the data.
        """

    @abstractmethod
    def receive(self) -> bytes:
        """Receive data from the server.

        Returns:
            The raw data received from the server.

        Raises:
            TransportError: When an error occurs while receiving the data.
        """


class SocketTransport(Transport):
    """Transport which uses socket to connect to the EPP server.

    Attributes:
        HEADER_SIZE: Size of the EPP message header in bytes. The header contains the size of the transmitted message.
        CHUNK_SIZE: Number of bytes to receive from the socket at a time.

    Args:
        hostname: Hostname of the EPP server.
        port: Port number.
        cert_file: Path to the certificate file.
        key_file: Path to the key file.
        password: Password to the key file.
        verify: Whether to verify a peer certificate.
                WARNING! Disabling this option is insecure and not recommended for production use.
    """

    HEADER_SIZE = 4
    CHUNK_SIZE = 1024

    def __init__(self, hostname: str, port: int, *, cert_file: PathType = None, key_file: PathType = None,
                 password: str = None, verify: bool = True):
        self.hostname = hostname
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        self.password = password
        self.verify = verify

        self.socket: Optional[ssl.SSLSocket] = None

    def connect(self) -> None:
        """Open the connection to the EPP server."""
        context = ssl.create_default_context()
        if self.cert_file is not None:
            context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file, password=self.password)
        if not self.verify:
            _LOGGER.warning("Verification of the peer certificate is disabled.")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((self.hostname, self.port))
        self.socket = context.wrap_socket(sock, server_hostname=self.hostname)

    def close(self) -> None:
        """Close the connection gracefully."""
        if self.socket is not None:
            self.socket.close()

    def send(self, message: bytes) -> None:
        """Send data to the server.

        Args:
            message: The message to be sent to the server.

        Raises:
            TransportError: When an error occurs while sending the data.
        """
        if self.socket is None:
            raise TransportError('Not connected to the server.')
        message_length = (len(message) + self.HEADER_SIZE).to_bytes(4, 'big')
        try:
            self.socket.sendall(message_length + message)
        except OSError as error:
            raise TransportError('Socket closed.') from error

    def receive(self) -> bytes:
        """Receive data from the server.

        Returns:
            Raw message received from the server.

        Raises:
            TransportError: When an error occurs while receiving the data.
        """
        if self.socket is None:
            raise TransportError('Not connected to the server.')

        try:
            header = self.socket.recv(self.HEADER_SIZE)
            expected_length = int.from_bytes(header, 'big') - self.HEADER_SIZE

            response = bytes()
            while len(response) < expected_length:
                response += self.socket.recv(min(self.CHUNK_SIZE, expected_length - len(response)))

            if response:
                return response

            raise TransportError('Empty response recieved.')

        except OSError as error:
            raise TransportError('Socket closed.') from error
