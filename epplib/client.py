#
# Copyright (C) 2021  CZ.NIC, z. s. p. o.
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

"""A client to send EPP commands and receive responses."""
from os import PathLike
from typing import Type, Union

from epplib.commands import Request
from epplib.responses import Response
from epplib.transport import Transport

PathType = Union[str, PathLike]


class Client:
    """A client to send EPP commands and receive responses.

    Attributes:
        transport: A transport object which is used for communication with the EPP server.
    """

    def __init__(self, transport: Transport):
        """Init the Client.

        Args:
            transport: A transport object which is used for communication with the EPP server.
        """
        self.transport = transport

    def __enter__(self):
        self.transport.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.transport.close()

    def send(self, request: Request) -> Response:
        """Send an EPP command and receive a response.

        Args:
            request: The command to be sent to the server.
        """
        message = request.xml()
        self.transport.send(message)

        return self.receive(request.response_class)

    def receive(self, response_class: Type[Response]) -> Response:
        """Receive a response from the server (possibly without sending a command).

        Args:
            response_class: A class to parse the response.
        """
        response_raw = self.transport.receive()
        response_parsed = response_class(response_raw)
        return response_parsed
