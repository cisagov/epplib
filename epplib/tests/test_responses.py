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
from typing import Mapping, cast
from unittest import TestCase

from lxml.builder import ElementMaker
from lxml.etree import Element, QName

from epplib.constants import NAMESPACE_EPP
from epplib.responses import Greeting, Response

BASE_DATA_PATH = Path(__file__).parent / 'data'
EM = ElementMaker(namespace=NAMESPACE_EPP, nsmap={'epp': NAMESPACE_EPP})


@dataclass
class DummyResponse(Response):

    tag: str

    @classmethod
    def parse(cls, raw_response) -> 'DummyResponse':
        return cast(DummyResponse, super().parse(raw_response))

    @classmethod
    def _parse_payload(cls, element: Element) -> Mapping[str, str]:
        return {'tag': element.tag}


class TestResponse(TestCase):
    def test_parse(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </epp>'''

        response = DummyResponse.parse(data)
        self.assertEqual(response.tag, QName(NAMESPACE_EPP, 'dummy'))

    def test_raise_if_not_epp(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <other xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </other>'''

        with self.assertRaisesRegex(ValueError, 'Root element has to be "epp"'):
            DummyResponse.parse(data)

    def test_find_text(self):
        element = EM.svcMenu(EM.lang('en'), EM.version())
        self.assertEqual(Response._find_text(element, './epp:lang'), 'en')
        self.assertEqual(Response._find_text(element, './epp:version'), '')
        self.assertIsNone(Response._find_text(element, './epp:missing'))

    def test_find_all_text(self):
        element = EM.svcMenu(EM.lang('en'), EM.lang('cs'), EM.version())
        self.assertEqual(Response._find_all_text(element, './epp:lang'), ['en', 'cs'])
        self.assertEqual(Response._find_all_text(element, './epp:version'), [''])
        self.assertEqual(Response._find_all_text(element, './epp:missing'), [])

    def test_find_child(self):
        element = EM.statement(EM.purpose(EM.admin()))
        self.assertEqual(Response._find_child(element, './epp:purpose'), 'admin')
        self.assertEqual(Response._find_child(element, './epp:recipient'), None)

    def test_find_children(self):
        element = EM.statement(EM.purpose(EM.admin(), EM.prov()))
        self.assertEqual(Response._find_children(element, './epp:purpose'), ['admin', 'prov'])
        self.assertEqual(Response._find_children(element, './epp:recipient'), [])


class TestGreeting(TestCase):
    path = BASE_DATA_PATH / 'greeting.xml'

    def test_parse(self):
        with open(self.path, 'br') as f:
            data = f.read()
        greeting = Greeting.parse(data)

        obj_uris = [
            'http://www.nic.cz/xml/epp/contact-1.6',
            'http://www.nic.cz/xml/epp/domain-1.4',
            'http://www.nic.cz/xml/epp/nsset-1.2',
            'http://www.nic.cz/xml/epp/keyset-1.3',
        ]

        self.assertEqual(greeting.sv_id, 'EPP server (DSDng)')
        self.assertEqual(greeting.sv_date, '2018-05-15T21:05:42+02:00')
        self.assertEqual(greeting.versions, ['1.0'])
        self.assertEqual(greeting.langs, ['en', 'cs'])
        self.assertEqual(greeting.obj_uris, obj_uris)
        self.assertEqual(greeting.ext_uris, ['http://www.nic.cz/xml/epp/enumval-1.2'])

        self.assertEqual(greeting.access, 'none')

        statement = Greeting.Statement(
            purpose=['admin', 'prov'],
            recipient=['public'],
            retention='stated',
            expiry='absolute'
        )
        self.assertEqual(greeting.statements, [statement])
