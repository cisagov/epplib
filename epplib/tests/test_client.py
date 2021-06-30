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
from typing import Type, cast
from unittest import TestCase
from unittest.mock import Mock, call

from lxml.etree import Element

from epplib.client import Client
from epplib.commands import Request
from epplib.responses import Response
from epplib.transport import Transport


class DummyTransport(Transport):

    raw_response = b'This is the Response!'

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def send(self, message: bytes) -> None:
        pass

    def receive(self) -> bytes:
        return self.raw_response


class DummyResponse(Response):
    def __init__(self, raw_response: bytes):
        self.raw_response = raw_response

    def _parse_payload(self, element) -> None:
        pass  # pragma: no cover


class DummyRequest(Request):

    raw_request = b'This is the Request!'

    def xml(self) -> bytes:
        return self.raw_request

    def _get_payload(self) -> Element:
        pass  # pragma: no cover

    @property
    def response_class(self) -> Type[Response]:
        return DummyResponse


class TestClient(TestCase):

    def test_context_manager(self):
        transport = Mock(spec=Transport)
        client = Client(transport)

        with client as cl:
            client.send(DummyRequest())

        self.assertEqual(client, cl)
        self.assertEqual(
            [call.connect(), call.send(DummyRequest.raw_request), call.receive(), call.close()],
            transport.mock_calls
        )

    def test_receive(self):
        client = Client(DummyTransport())

        with client:
            response = client.receive(DummyResponse)

        self.assertEqual(type(response), DummyResponse)
        self.assertEqual(cast(DummyResponse, response).raw_response, DummyTransport.raw_response)

    def test_send(self):
        transport = Mock(wraps=DummyTransport())
        client = Client(transport)

        with client:
            command = DummyRequest()
            response = client.send(command)

        transport.send.assert_called_with(DummyRequest.raw_request)

        self.assertEqual(type(response), DummyResponse)
        self.assertEqual(cast(DummyResponse, response).raw_response, DummyTransport.raw_response)
