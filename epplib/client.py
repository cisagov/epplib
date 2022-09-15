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

"""A client to send EPP commands and receive responses."""
import logging
from datetime import datetime
from os import PathLike
from random import choices
from string import ascii_lowercase, digits
from types import TracebackType
from typing import Optional, Type, Union

from lxml.etree import XMLSchema

from epplib.commands import Request
from epplib.responses import Greeting, Response
from epplib.transport import Transport

PathType = Union[str, PathLike]
LOGGER = logging.getLogger(__name__)


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

    def __enter__(self) -> 'Client':
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        self.close()

    def connect(self) -> None:
        """Open the connection to the EPP server.

        After the connection is opened the server sends Greeting which is automaticaly received and stored.
        """
        self.transport.connect()
        self._receive(Greeting)

    def close(self) -> None:
        """Close the connection gracefully."""
        self.transport.close()

    def send(self, request: Request) -> Response:
        """Send an EPP command and receive a response.

        Args:
            request: The command to be sent to the server.
        """
        tr_id = self._genereate_tr_id()
        message = request.xml(tr_id=tr_id, schema=self.schema)
        self._log_raw_xml(message)
        self.transport.send(message)

        response = self._receive(request.response_class)
        if hasattr(response, 'cl_tr_id') and (response.cl_tr_id != tr_id):  # type: ignore[attr-defined]
            log_message = 'clTRID of the response ({}) differs from the clTRID of the request ({}).'
            LOGGER.warning(log_message.format(response.cl_tr_id, tr_id))  # type: ignore[attr-defined]
        return response

    def _receive(self, response_class: Type[Response]) -> Response:
        """Receive a response from the server (possibly without sending a command).

        Args:
            response_class: A class to parse the response.
        """
        response_raw = self.transport.receive()
        self._log_raw_xml(response_raw)
        response_parsed = response_class.parse(response_raw, self.schema)

        if isinstance(response_parsed, Greeting):
            self.greeting = response_parsed

        return response_parsed

    def _genereate_tr_id(self) -> str:
        random = ''.join(choices(ascii_lowercase + digits, k=6))  # nosec - Not a security feature.
        timestamp = datetime.now().isoformat()
        return '{}#{}'.format(random, timestamp)

    def _log_raw_xml(self, xml: bytes) -> None:
        """Log raw xml, try converting it to UTF-8."""
        try:
            xml_final: Union[str, bytes] = str(xml, encoding="utf-8")
        except UnicodeDecodeError:
            xml_final = xml

        LOGGER.debug(xml_final)
