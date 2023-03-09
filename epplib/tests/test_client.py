#
# Copyright (C) 2021-2023  CZ.NIC, z. s. p. o.
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
from typing import Any, Dict, Optional, cast
from unittest import TestCase
from unittest.mock import Mock, call, patch

from freezegun import freeze_time
from lxml.etree import Element, XMLSchema
from testfixtures import LogCapture

from epplib.client import Client
from epplib.commands import Request
from epplib.responses import Greeting, Response, Result
from epplib.transport import Transport

GREETING = (Path(__file__).parent / 'data/responses/greeting_template.xml').read_bytes().replace(b'{expiry}', b'')


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
    def parse(cls, raw_response: bytes, schema: Optional[XMLSchema] = None) -> 'DummyResponse':
        return cls(raw_response=raw_response, schema=schema)

    @classmethod
    def _extract_payload(cls, element: Element) -> Dict[str, Any]:  # type: ignore[empty-body]
        pass  # pragma: no cover


class DummyRequest(Request):

    response_class = DummyResponse
    raw_request = b'This is the Request!'

    def xml(self, tr_id: Optional[str] = None, schema: Optional[XMLSchema] = None) -> bytes:
        self.tr_id = tr_id
        self.schema = schema
        return self.raw_request

    def _get_payload(self, tr_id: Optional[str]) -> Element:
        pass  # pragma: no cover


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
        self.assertEqual(cast(Greeting, client.greeting).sv_id, 'EPP server (DSDng)')

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

    @freeze_time('2021-05-04 12:21')
    @patch('epplib.client.choices')
    def test_send(self, mock_choices):
        transport = Mock(wraps=DummyTransport())
        mock_schema = Mock(spec=XMLSchema)
        mock_schema.assertValid = Mock()  # Otherwise we get AttributeError: Attributes cannot start with 'assert'
        mock_choices.side_effect = lambda x, k: x[:k]

        client = Client(transport, mock_schema)

        with client:
            request = DummyRequest()
            response = client.send(request)

        self.assertEqual(request.schema, mock_schema)
        self.assertEqual(request.tr_id, 'abcdef#2021-05-04T12:21:00')

        transport.send.assert_called_with(DummyRequest.raw_request)

        self.assertEqual(type(response), DummyResponse)
        self.assertEqual(cast(DummyResponse, response).raw_response, DummyTransport.raw_response)

    @freeze_time('2021-05-04 12:21')
    @patch('epplib.client.choices')
    def test_send_custom_tr_id(self, mock_choices):
        transport = Mock(wraps=DummyTransport())
        mock_schema = Mock(spec=XMLSchema)
        mock_schema.assertValid = Mock()  # Otherwise we get AttributeError: Attributes cannot start with 'assert'
        client = Client(transport, mock_schema)

        with client:
            request = DummyRequest()
            response = client.send(request, tr_id='Gazpacho!')

        self.assertEqual(request.tr_id, 'Gazpacho!')
        self.assertEqual(type(response), DummyResponse)
        # Check choices were not called.
        self.assertEqual(mock_choices.mock_calls, [])

    @patch('epplib.client.Client._genereate_tr_id')
    @patch('epplib.client.Client._receive')
    def test_cl_tr_id_check_warning(self, mock_receive, mock_generate_id):
        transport = Mock(wraps=DummyTransport())
        mock_generate_id.return_value = 'abc'
        mock_receive.return_value = Result(code=1000, msg='Message', res_data=[], cl_tr_id='Wrong', sv_tr_id='00001')

        client = Client(transport, None)
        request = DummyRequest()
        with client:
            with LogCapture(propagate=False) as log_handler:
                client.send(request)

        mock_receive.assert_called()
        log_handler.check(
            ('epplib.client', 'DEBUG', 'This is the Request!'),
            ('epplib.client', 'WARNING', 'clTRID of the response (Wrong) differs from the clTRID of the request (abc).')
        )

    @patch('epplib.client.Client._genereate_tr_id')
    @patch('epplib.client.Client._receive')
    def test_cl_tr_id_check_correct(self, mock_receive, mock_generate_id):
        transport = Mock(wraps=DummyTransport())
        mock_generate_id.return_value = 'expected'
        mock_receive.return_value = Result(code=1000, msg='Message', res_data=[], cl_tr_id='expected', sv_tr_id='00001')

        client = Client(transport, None)
        request = DummyRequest()
        with client:
            with LogCapture(propagate=False, level=3) as log_handler:
                client.send(request)

        mock_receive.assert_called()
        log_handler.check(
            ('epplib.client', 'DEBUG', 'This is the Request!')
        )

    @patch('epplib.client.Client._genereate_tr_id')
    @patch('epplib.client.Client._receive')
    def test_cl_tr_id_check_not_expected(self, mock_receive, mock_generate_id):
        transport = Mock(wraps=DummyTransport())
        mock_generate_id.return_value = 'expected'
        mock_receive.return_value = DummyResponse(b'0', None)

        client = Client(transport, None)
        request = DummyRequest()
        with client:
            with LogCapture(propagate=False) as log_handler:
                client.send(request)

        mock_receive.assert_called()
        log_handler.check(
            ('epplib.client', 'DEBUG', 'This is the Request!')
        )

    @patch('epplib.client.Client._genereate_tr_id')
    @patch('epplib.client.Client._receive')
    def test_log_raw_xml_error(self, mock_receive, mock_generate_id):
        transport = Mock(wraps=DummyTransport())

        client = Client(transport, None)
        with LogCapture(propagate=False) as log_handler:
            client._log_raw_xml(b'\xff')

        log_handler.check(
            ('epplib.client', 'DEBUG', "b'\\xff'")
        )
