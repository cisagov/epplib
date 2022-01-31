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

from dataclasses import dataclass
from typing import Any, Dict
from unittest import TestCase

from lxml.etree import DocumentInvalid, Element, QName, fromstring

from epplib.commands import Hello, Login, Logout, Request
from epplib.commands.base import Command
from epplib.commands.command_extensions import CommandExtension
from epplib.constants import NAMESPACE
from epplib.responses import Response
from epplib.tests.utils import EM, SCHEMA, XMLTestCase, make_epp_root

DUMMY_NAMESPACE = 'dummy:name:space'
EXTENSION_NAMESPACE = 'extension:name:space'


class DummyResponse(Response):
    @classmethod
    def _parse_payload(cls, element: Element) -> Dict[str, Any]:
        return dict()  # pragma: no cover


class DummyRequest(Request):
    response_class = DummyResponse

    def _get_payload(self, tr_id: str = None) -> Element:
        return Element(QName(DUMMY_NAMESPACE, 'dummy'))


@dataclass
class DummyCommand(Command):
    response_class = DummyResponse

    def _get_command_payload(self) -> Element:
        return Element(QName(DUMMY_NAMESPACE, 'dummy'))


@dataclass
class DummyCommandExtension(CommandExtension):

    def get_payload(self) -> Element:
        return Element(QName(EXTENSION_NAMESPACE, 'dummy_ext'))


class TestRequest(TestCase):
    def test_xml_header(self):
        self.assertTrue(DummyRequest().xml().startswith(b"<?xml version='1.0' encoding='utf-8'?>\n"))

    def test_root_tag(self):
        root = fromstring(DummyRequest().xml())
        self.assertEqual(root.tag, QName(NAMESPACE.EPP, 'epp'))

    def test_schema_location(self):
        root = fromstring(DummyRequest().xml())
        expected = {
            QName(NAMESPACE.XSI, 'schemaLocation'): 'urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd'
        }
        self.assertEqual(root.attrib, expected)

    def test_get_content(self):
        root = fromstring(DummyRequest().xml())
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, QName(DUMMY_NAMESPACE, 'dummy'))

    def test_validate(self):
        with self.assertRaises(DocumentInvalid):
            DummyRequest().xml(schema=SCHEMA)


class TestHello(XMLTestCase):
    def test_valid(self):
        self.assertRequestValid(Hello, {})

    def test_xml(self):
        root = fromstring(Hello().xml())
        expected = make_epp_root(EM.hello())
        self.assertXMLEqual(root, expected)


class TestCommand(XMLTestCase):
    def test_command_no_extension(self):
        root = fromstring(DummyCommand().xml())
        expected = make_epp_root(
            EM.command(
                EM(str(QName(DUMMY_NAMESPACE, 'dummy'))),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_command_extension(self):
        command = DummyCommand()
        command.add_extension(DummyCommandExtension())
        root = fromstring(command.xml())
        expected = make_epp_root(
            EM.command(
                EM(str(QName(DUMMY_NAMESPACE, 'dummy'))),
                EM.extension(
                    EM(str(QName(EXTENSION_NAMESPACE, 'dummy_ext')))
                )
            )
        )
        self.assertXMLEqual(root, expected)

    def test_command_tr_id(self):
        tr_id = 'tr_id_123'
        root = fromstring(DummyCommand().xml(tr_id=tr_id))

        expected = make_epp_root(
            EM.command(
                EM(str(QName(DUMMY_NAMESPACE, 'dummy'))),
                EM.clTRID(tr_id),
            )
        )
        self.assertXMLEqual(root, expected)


class TestLogin(XMLTestCase):

    params: Dict[str, Any] = {
        'cl_id': 'client id',
        'password': '1234567890',
        'new_pw': 'qwerty',
        'version': '1.0',
        'lang': 'cs',
        'obj_uris': ['http://www.nic.cz/xml/epp/contact-1.6', 'http://www.nic.cz/xml/epp/nsset-1.2'],
        'ext_uris': ['http://www.nic.cz/xml/epp/enumval-1.2'],
    }

    def test_valid_all_params(self):
        self.assertRequestValid(Login, self.params)

    def test_valid_required_params_only(self):
        self.assertRequestValid(Login, {k: self.params[k] for k in ['cl_id', 'password', 'obj_uris']})

    def test_xml_full(self):
        root = fromstring(Login(**self.params).xml())
        expected = make_epp_root(
            EM.command(
                EM.login(
                    EM.clID(self.params['cl_id']),
                    EM.pw(self.params['password']),
                    EM.newPW(self.params['new_pw']),
                    EM.options(
                        EM.version(self.params['version']),
                        EM.lang(self.params['lang']),
                    ),
                    EM.svcs(
                        *[EM.objURI(item) for item in self.params['obj_uris']],
                        EM.svcExtension(
                            *[EM.extURI(item) for item in self.params['ext_uris']],
                        ),
                    ),
                ),
            ),
        )
        self.assertXMLEqual(root, expected)

    def test_xml_minimal(self):
        minimal_params = {k: self.params[k] for k in ['cl_id', 'password', 'obj_uris']}
        root = fromstring(Login(**minimal_params).xml())
        expected = make_epp_root(
            EM.command(
                EM.login(
                    EM.clID(self.params['cl_id']),
                    EM.pw(self.params['password']),
                    EM.options(
                        EM.version('1.0'),
                        EM.lang('en'),
                    ),
                    EM.svcs(
                        *[EM.objURI(item) for item in self.params['obj_uris']],
                    ),
                ),
            ),
        )
        self.assertXMLEqual(root, expected)


class TestLogout(XMLTestCase):

    def test_valid(self):
        self.assertRequestValid(Logout, {})

    def test_xml(self):
        root = fromstring(Logout().xml())
        expected = make_epp_root(EM.command(EM.logout))
        self.assertXMLEqual(root, expected)
