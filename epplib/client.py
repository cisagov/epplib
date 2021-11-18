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
from datetime import datetime
from os import PathLike
from random import choices
from string import ascii_lowercase, digits
from typing import Optional, Type, Union

from lxml.etree import XMLSchema

from epplib.commands import Request
from epplib.responses import Greeting, Response
from epplib.transport import Transport

PathType = Union[str, PathLike]


class Client:
    """A client to send EPP commands and receive responses.

    Attributes:
        transport: A transport object which is used for communication with the EPP server.
        schema: A XML schema used to validate Responses. No validation is done if schema is None.
        greeting: The last Greeting received from the EPP server. None if no Greeting was received yet.
    """

    def __init__(self, transport: Transport, schema: XMLSchema = None):
        """Init the Client.

        Args:
            transport: A transport object which is used for communication with the EPP server.
            schema: A XML schema used to validate Responses. No validation is done if schema is None.
        """
        self.transport = transport
        self.schema = schema
        self.greeting: Optional[Greeting] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Open the connection to the EPP server.

        After the connection is opened the server sends Greeting which is automaticaly received and stored.
        """
        self.transport.connect()
        self._receive(Greeting)

    def close(self):
        """Close the connection gracefully."""
        self.transport.close()

    def send(self, request: Request) -> Response:
        """Send an EPP command and receive a response.

        Args:
            request: The command to be sent to the server.
        """
        message = request.xml(tr_id=self._genereate_tr_id(), schema=self.schema)
        self.transport.send(message)

        return self._receive(request.response_class)

    def _receive(self, response_class: Type[Response]) -> Response:
        """Receive a response from the server (possibly without sending a command).

        Args:
            response_class: A class to parse the response.
        """
        response_raw = self.transport.receive()
        response_parsed = response_class.parse(response_raw, self.schema)

        if isinstance(response_parsed, Greeting):
            self.greeting = response_parsed

        return response_parsed

    def _genereate_tr_id(self) -> str:
        random = ''.join(choices(ascii_lowercase + digits, k=6))  # nosec - Not a security feature.
        timestamp = datetime.now().isoformat()
        return '{}#{}'.format(random, timestamp)
