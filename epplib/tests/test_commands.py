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

from pathlib import Path
from typing import Any, Dict, List, Type
from unittest import TestCase

from lxml.etree import DocumentInvalid, Element, QName, XMLSchema, fromstring

from epplib.commands import Command, Hello, Login, Request
from epplib.constants import NAMESPACE_EPP, NAMESPACE_XSI
from epplib.responses import Response
from epplib.utils import safe_parse

DUMMY_NAMESPACE = 'dummy:name:space'
NSMAP = {'epp': NAMESPACE_EPP, 'dm': DUMMY_NAMESPACE}

SCHEMA = XMLSchema(file=str(Path(__file__).parent / 'data/schemas/all-2.4.1.xsd'))


def assert_request_valid(request_class: Type[Request], params):
    """Assert that the generated XML complies with the schema."""
    request = request_class(**params)  # type: ignore
    xml = request.xml(tr_id='tr_id_123')
    SCHEMA.assertValid(safe_parse(xml))


class DummyResponse(Response):
    @classmethod
    def _parse_payload(csl, element) -> Dict[str, Any]:
        return dict()  # pragma: no cover


class DummyRequest(Request):
    response_class = DummyResponse

    def _get_payload(self, tr_id: str = None) -> Element:
        return Element(QName(DUMMY_NAMESPACE, 'dummy'))


class DummyCommand(Command):
    response_class = DummyResponse

    def _get_command_payload(self) -> Element:
        return Element(QName(DUMMY_NAMESPACE, 'dummy'))


class TestRequest(TestCase):
    def test_xml_header(self):
        self.assertTrue(DummyRequest().xml().startswith(b"<?xml version='1.0' encoding='utf-8'?>\n"))

    def test_root_tag(self):
        root = fromstring(DummyRequest().xml())
        self.assertEqual(root.tag, QName(NAMESPACE_EPP, 'epp'))

    def test_schema_location(self):
        root = fromstring(DummyRequest().xml())
        expected = {
            QName(NAMESPACE_XSI, 'schemaLocation'): 'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'
        }
        self.assertEqual(root.attrib, expected)

    def test_get_content(self):
        root = fromstring(DummyRequest().xml())
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, QName(DUMMY_NAMESPACE, 'dummy'))

    def test_validate(self):
        with self.assertRaises(DocumentInvalid):
            DummyRequest().xml(schema=SCHEMA)


class TestHello(TestCase):
    def test_valid(self):
        assert_request_valid(Hello, {})

    def test_tag(self):
        root = fromstring(Hello().xml())
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, QName(NAMESPACE_EPP, 'hello'))

    def test_has_no_content(self):
        root = fromstring(Hello().xml())
        hello = root[0]
        self.assertEqual(len(hello), 0)
        self.assertEqual(len(hello.attrib), 0)


class TestCommand(TestCase):
    def test_command(self):
        root = fromstring(DummyCommand().xml())
        command = root[0]

        self.assertEqual(command.tag, QName(NAMESPACE_EPP, 'command'))
        self.assertEqual(len(command), 1)
        self.assertEqual(len(command.attrib), 0)

        self.assertEqual(command[0].tag, QName(DUMMY_NAMESPACE, 'dummy'))

    def test_command_tr_id(self):
        tr_id = 'tr_id_123'
        root = fromstring(DummyCommand().xml(tr_id=tr_id))
        command = root[0]

        self.assertEqual(command.tag, QName(NAMESPACE_EPP, 'command'))
        self.assertEqual(len(command), 2)
        self.assertEqual(len(command.attrib), 0)

        self.assertEqual(
            [element.tag for element in command.findall('./dm:dummy', namespaces=NSMAP)],
            [QName(DUMMY_NAMESPACE, 'dummy')]
        )
        self.assertEqual(
            [element.text for element in command.findall('./epp:clTRID', namespaces=NSMAP)],
            [tr_id]
        )


class TestLogin(TestCase):

    params: Dict[str, Any] = {
        'cl_id': 'client id',
        'password': '1234567890',
        'new_password': 'qwerty',
        'version': '1.0',
        'lang': 'cs',
        'obj_uris': ['http://www.nic.cz/xml/epp/contact-1.6', 'http://www.nic.cz/xml/epp/nsset-1.2'],
        'ext_uris': ['http://www.nic.cz/xml/epp/enumval-1.2'],
    }

    def _assert_element(self, root: Element, path: str, text: str = None, attrib: Dict[str, Any] = None):
        found = root.findall(path, namespaces=NSMAP)
        self.assertEqual(len(found), 1)
        element = found[0]
        self.assertEqual(element.attrib, attrib or {})
        self.assertEqual(element.text, text)

    def _assert_many_elements(self, root: Element, path: str, text: List[str] = None):
        found = root.findall(path, namespaces=NSMAP)
        self.assertEqual(sorted(text or []), sorted([element.text for element in found]))
        for element in found:
            self.assertEqual(element.attrib, {})

    def _assert_not_present(self, root: Element, path: str):
        found = root.findall(path, namespaces=NSMAP)
        self.assertEqual(len(found), 0)

    def test_valid_all_params(self):
        assert_request_valid(Login, self.params)

    def test_valid_required_params_only(self):
        assert_request_valid(Login, {k: self.params[k] for k in ['cl_id', 'password', 'obj_uris']})

    def test_data_full(self):
        root = fromstring(Login(**self.params).xml())
        self._assert_element(root, './epp:command/epp:login')
        self._assert_element(root, './epp:command/epp:login/epp:clID', self.params['cl_id'])
        self._assert_element(root, './epp:command/epp:login/epp:pw', self.params['password'])
        self._assert_element(root, './epp:command/epp:login/epp:newPW', self.params['new_password'])
        self._assert_element(root, './epp:command/epp:login/epp:options/epp:version', self.params['version'])
        self._assert_element(root, './epp:command/epp:login/epp:options/epp:lang', self.params['lang'])
        self._assert_many_elements(root, './epp:command/epp:login/epp:svcs/epp:objURI', self.params['obj_uris'])
        self._assert_many_elements(
            root, './epp:command/epp:login/epp:svcs/epp:svcExtension/epp:extURI', self.params['ext_uris']
        )

    def test_data_minimal(self):
        minimal_params = {k: self.params[k] for k in ['cl_id', 'password', 'obj_uris']}
        root = fromstring(Login(**minimal_params).xml())
        self._assert_element(root, './epp:command/epp:login')
        self._assert_element(root, './epp:command/epp:login/epp:clID', self.params['cl_id'])
        self._assert_element(root, './epp:command/epp:login/epp:pw', self.params['password'])
        self._assert_not_present(root, './epp:command/epp:login/epp:newPW')
        self._assert_element(root, './epp:command/epp:login/epp:options/epp:version', '1.0')
        self._assert_element(root, './epp:command/epp:login/epp:options/epp:lang', 'en')
        self._assert_many_elements(root, './epp:command/epp:login/epp:svcs/epp:objURI', self.params['obj_uris'])
        self._assert_not_present(root, './epp:command/epp:login/epp:svcs/epp:svcExtension/epp:extURI')
