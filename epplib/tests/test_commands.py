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

from unittest import TestCase

from lxml.etree import Element, QName, fromstring

from epplib.commands import Hello, Request
from epplib.constants import NAMESPACE_EPP, NAMESPACE_XSI
from epplib.responses import Response


class DummyResponse(Response):
    def _parse_payload(self, element) -> None:
        pass  # pragma: no cover


class DummyRequest(Request):
    response_class = DummyResponse

    def _get_payload(self) -> Element:
        return Element('dummy')


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
        self.assertEqual(root[0].tag, QName(NAMESPACE_EPP, 'dummy'))


class TestHello(TestCase):
    def test_tag(self):
        root = fromstring(Hello().xml())
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, QName(NAMESPACE_EPP, 'hello'))

    def test_has_no_content(self):
        root = fromstring(Hello().xml())
        hello = root[0]
        self.assertEqual(len(hello), 0)
        self.assertEqual(len(hello.attrib), 0)
