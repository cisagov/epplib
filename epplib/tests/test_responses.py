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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping, cast
from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time
from isodate import parse_datetime
from lxml.builder import ElementMaker
from lxml.etree import DocumentInvalid, Element, QName, XMLSchema

from epplib.constants import NAMESPACE_EPP
from epplib.responses import Greeting, ParsingError, Response

BASE_DATA_PATH = Path(__file__).parent / 'data'
SCHEMA = XMLSchema(file=str(BASE_DATA_PATH / 'schemas/all-2.4.1.xsd'))

EM = ElementMaker(namespace=NAMESPACE_EPP, nsmap={'epp': NAMESPACE_EPP})


@dataclass
class DummyResponse(Response):

    tag: str

    @classmethod
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'DummyResponse':
        return cast(DummyResponse, super().parse(raw_response, schema))

    @classmethod
    def _parse_payload(cls, element: Element) -> Mapping[str, str]:
        return {'tag': element.tag}


class TestParsingError(TestCase):
    def test_str(self):
        self.assertEqual(str(ParsingError()), '')
        self.assertEqual(str(ParsingError('Gazpacho!')), 'Gazpacho!')
        self.assertEqual(str(ParsingError(raw_response='Gazpacho!')), "Raw response:\n'Gazpacho!'")


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

    def test_parse_with_schema(self):
        invalid = b'''<?xml version="1.0" encoding="UTF-8"?>
                      <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                          <invalid/>
                      </epp>'''

        message = "Element '{urn:ietf:params:xml:ns:epp-1.0}invalid': This element is not expected\\."
        with self.assertRaisesRegex(DocumentInvalid, message):
            DummyResponse.parse(invalid, SCHEMA)

    @patch('epplib.tests.test_responses.DummyResponse._parse_payload')
    def test_wrap_exceptions(self, mock_parse):
        mock_parse.side_effect = ValueError('It is broken!')
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </epp>'''
        with self.assertRaisesRegex(ParsingError, '<dummy\\/>'):
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
    greeting_template = (BASE_DATA_PATH / 'greeting_template.xml').read_bytes()

    expiry_absolute = b'<expiry><absolute>2021-05-04T03:14:15+02:00</absolute></expiry>'
    expiry_relative = b'<expiry><relative>P0Y0M1DT10H15M20S</relative></expiry>'

    def test_parse(self):
        xml = self.greeting_template.replace(b'{expiry}', self.expiry_absolute)
        greeting = Greeting.parse(xml, SCHEMA)

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
        self.assertEqual(greeting.expiry, datetime(2021, 5, 4, 3, 14, 15, tzinfo=timezone(timedelta(hours=2))))

        statement = Greeting.Statement(
            purpose=['admin', 'prov'],
            recipient=['public'],
            retention='stated',
        )
        self.assertEqual(greeting.statements, [statement])

    def test_parse_expiry_absolute(self):
        xml = self.greeting_template.replace(b'{expiry}', self.expiry_absolute)
        greeting = Greeting.parse(xml, SCHEMA)

        expected = datetime(2021, 5, 4, 3, 14, 15, tzinfo=timezone(timedelta(hours=2)))
        self.assertEqual(greeting.expiry, expected)

    @freeze_time('2021-07-14 12:15')
    def test_parse_expiry_relative(self):
        xml = self.greeting_template.replace(b'{expiry}', self.expiry_relative)
        greeting = Greeting.parse(xml, SCHEMA)

        expected = timedelta(days=1, hours=10, minutes=15, seconds=20)
        self.assertEqual(greeting.expiry, expected)

    def test_parse_no_expiry(self):
        xml = self.greeting_template.replace(b'{expiry}', b'')
        greeting = Greeting.parse(xml, SCHEMA)

        self.assertEqual(greeting.expiry, None)

    @freeze_time('2021-07-14 12:15')
    def test_parse_expiry_duration_conversion(self):
        # isodate parses time period to timedelta or Duration depending on whether it contains "complicated" intervals.

        expiry_absolute = EM.expiry(EM.absolute('2021-05-04T03:14:15+02:00'))
        self.assertEqual(
            Greeting._parse_expiry(expiry_absolute),
            datetime(2021, 5, 4, 3, 14, 15, tzinfo=timezone(timedelta(hours=2)))
        )

        expiry_relative_simple = EM.expiry(EM.relative('P0Y0M1DT10H15M20S'))
        self.assertEqual(
            Greeting._parse_expiry(expiry_relative_simple),
            timedelta(days=1, hours=10, minutes=15, seconds=20)
        )

        expiry_relative_complicated = EM.expiry(EM.relative('P1Y2M3DT4H5M6S'))
        self.assertEqual(
            Greeting._parse_expiry(expiry_relative_complicated),
            parse_datetime('2022-09-17T16:20:06') - parse_datetime('2021-07-14T12:15')
        )

    def test_parse_absolute_expiry_error(self):
        expiry = EM.expiry(EM.absolute('Gazpacho!'))
        with self.assertRaisesRegex(ParsingError, 'Could not parse "Gazpacho!" as absolute expiry\\.'):
            Greeting._parse_expiry(expiry)

    def test_parse_relative_expiry_error(self):
        expiry = EM.expiry(EM.relative('Gazpacho!'))
        with self.assertRaisesRegex(ParsingError, 'Could not parse "Gazpacho!" as relative expiry\\.'):
            Greeting._parse_expiry(expiry)

    def test_parse_expiry_invalid_tag(self):
        expiry = EM.expiry(EM.invalid('2021-05-04T03:14:15+02:00'))
        message = 'Expected expiry specification. Found "{urn:ietf:params:xml:ns:epp-1.0}invalid" instead\\.'
        with self.assertRaisesRegex(ValueError, message):
            Greeting._parse_expiry(expiry)
