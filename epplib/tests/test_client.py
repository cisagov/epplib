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
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Type, cast
from unittest import TestCase
from unittest.mock import Mock, call

from lxml.etree import Element, XMLSchema

from epplib.client import Client
from epplib.commands import Request
from epplib.responses import Greeting, Response
from epplib.transport import Transport

GREETING = (Path(__file__).parent / 'data/greeting_template.xml').read_bytes().replace(b'{expiry}', b'')


class DummyTransport(Transport):

    greeting_sent = False
    raw_response = b'This is the Response!'

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def send(self, message: bytes) -> None:
        pass

    def receive(self) -> bytes:
        if not self.greeting_sent:
            self.greeting_sent = True
            return GREETING
        return self.raw_response


@dataclass
class DummyResponse(Response):

    raw_response: bytes
    schema: XMLSchema

    @classmethod
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'DummyResponse':
        return cls(raw_response=raw_response, schema=schema)

    @classmethod
    def _extract_payload(cls, element: Element) -> Dict[str, Any]:
        pass  # pragma: no cover


class DummyRequest(Request):

    raw_request = b'This is the Request!'

    def xml(self, schema: XMLSchema = None) -> bytes:
        self.schema = schema
        return self.raw_request

    def _get_payload(self) -> Element:
        pass  # pragma: no cover

    @property
    def response_class(self) -> Type[Response]:
        return DummyResponse


class TestClient(TestCase):

    def test_context_manager(self):
        transport = Mock(spec=Transport)
        transport.receive.return_value = GREETING
        client = Client(transport)

        with client as cl:
            client.send(DummyRequest())

        self.assertEqual(client, cl)
        self.assertEqual(
            [call.connect(), call.receive(), call.send(DummyRequest.raw_request), call.receive(), call.close()],
            transport.mock_calls
        )

    def test_connect(self):
        transport = Mock(spec=Transport)
        transport.receive.return_value = GREETING

        client = Client(transport)
        client.connect()
        self.assertEqual(transport.mock_calls, [call.connect(), call.receive()])
        self.assertIsInstance(client.greeting, Greeting)
        self.assertEqual(client.greeting.sv_id, 'EPP server (DSDng)')  # type: ignore

    def test_close(self):
        transport = Mock(spec=Transport)
        transport.receive.return_value = GREETING

        client = Client(transport)

        client.connect()
        client.close()
        self.assertEqual(transport.mock_calls, [call.connect(), call.receive(), call.close()])

    def test_receive(self):
        mock_schema = Mock(spec=XMLSchema)
        mock_schema.assertValid = Mock()  # Otherwise we get AttributeError: Attributes cannot start with 'assert'
        client = Client(DummyTransport(), mock_schema)

        with client:
            response = client._receive(DummyResponse)

        self.assertEqual(type(response), DummyResponse)
        self.assertEqual(cast(DummyResponse, response).raw_response, DummyTransport.raw_response)
        self.assertEqual(cast(DummyResponse, response).schema, mock_schema)

    def test_send(self):
        transport = Mock(wraps=DummyTransport())
        mock_schema = Mock(spec=XMLSchema)
        mock_schema.assertValid = Mock()  # Otherwise we get AttributeError: Attributes cannot start with 'assert'
        client = Client(transport, mock_schema)

        with client:
            request = DummyRequest()
            response = client.send(request)

        self.assertEqual(request.schema, mock_schema)

        transport.send.assert_called_with(DummyRequest.raw_request)

        self.assertEqual(type(response), DummyResponse)
        self.assertEqual(cast(DummyResponse, response).raw_response, DummyTransport.raw_response)
