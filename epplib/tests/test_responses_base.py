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
from typing import ClassVar, Mapping, cast
from unittest import TestCase
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from lxml.builder import ElementMaker
from lxml.etree import DocumentInvalid, Element, QName, XMLSchema
from testfixtures import LogCapture

from epplib.constants import NAMESPACE
from epplib.responses import Greeting, ParsingError, Response, Result
from epplib.responses.base import EXTENSIONS
from epplib.responses.extensions import ResponseExtension
from epplib.tests.utils import BASE_DATA_PATH, EM, SCHEMA


@dataclass
class DummyResponse(Response):

    _payload_tag: ClassVar = QName(NAMESPACE.EPP, 'dummy')
    payload: str

    @classmethod
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'DummyResponse':
        return cast(DummyResponse, super().parse(raw_response, schema))

    @classmethod
    def _extract_payload(cls, element: Element) -> Mapping[str, str]:
        return {'payload': element.tag}


@dataclass
class DummyExtension(ResponseExtension):

    tag = QName('dummy', 'dummyExtension')
    text: str

    @classmethod
    def extract(cls, element: Element) -> 'DummyExtension':
        return cls(element.text)


@dataclass
class OtherExtension(ResponseExtension):

    tag = QName('dummy', 'otherExtension')
    value: int

    @classmethod
    def extract(cls, element: Element) -> 'OtherExtension':
        return cls(int(element.attrib['value']))


class TestResponse(TestCase):
    def test_parse(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </epp>'''

        response = DummyResponse.parse(data)
        self.assertEqual(response.payload, QName(NAMESPACE.EPP, 'dummy'))

    def test_raise_if_not_epp(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <other xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </other>'''

        with self.assertRaisesRegex(ValueError, 'Root element has to be "epp"'):
            DummyResponse.parse(data)

    def test_raise_if_unexpected_tag(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <unexpected/>
                   </epp>'''

        message = 'Expected {} tag\\. Found {} instead\\.'.format(
            QName(NAMESPACE.EPP, 'dummy'),
            QName(NAMESPACE.EPP, 'unexpected')
        )
        with self.assertRaisesRegex(ValueError, message):
            DummyResponse.parse(data)

    def test_parse_with_schema(self):
        invalid = b'''<?xml version="1.0" encoding="UTF-8"?>
                      <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                          <invalid/>
                      </epp>'''

        message = "Element '{urn:ietf:params:xml:ns:epp-1.0}invalid': This element is not expected\\."
        with self.assertRaisesRegex(DocumentInvalid, message):
            DummyResponse.parse(invalid, SCHEMA)

    @patch('epplib.tests.test_responses_base.DummyResponse._extract_payload')
    def test_wrap_exceptions(self, mock_parse):
        mock_parse.side_effect = ValueError('It is broken!')
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
                       <dummy/>
                   </epp>'''
        with self.assertRaisesRegex(ParsingError, '<dummy\\/>'):
            DummyResponse.parse(data)


class TestGreeting(TestCase):
    greeting_template = (BASE_DATA_PATH / 'responses/greeting_template.xml').read_bytes()

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

    def test_parse_expiry_relative(self):
        xml = self.greeting_template.replace(b'{expiry}', self.expiry_relative)
        greeting = Greeting.parse(xml, SCHEMA)

        expected = relativedelta(days=1, hours=10, minutes=15, seconds=20)
        self.assertEqual(greeting.expiry, expected)

    def test_parse_no_expiry(self):
        xml = self.greeting_template.replace(b'{expiry}', b'')
        greeting = Greeting.parse(xml, SCHEMA)

        self.assertEqual(greeting.expiry, None)

    def test_extract_absolute_expiry_error(self):
        expiry = EM.expiry(EM.absolute('Gazpacho!'))
        with self.assertRaisesRegex(ParsingError, 'Could not parse "Gazpacho!" as absolute expiry\\.'):
            Greeting._extract_expiry(expiry)

    def test_extract_relative_expiry_error(self):
        expiry = EM.expiry(EM.relative('Gazpacho!'))
        with self.assertRaisesRegex(ParsingError, 'Could not parse "Gazpacho!" as relative expiry\\.'):
            Greeting._extract_expiry(expiry)

    def test_extract_expiry_invalid_tag(self):
        expiry = EM.expiry(EM.invalid('2021-05-04T03:14:15+02:00'))
        message = 'Expected expiry specification. Found "{urn:ietf:params:xml:ns:epp-1.0}invalid" instead\\.'
        with self.assertRaisesRegex(ValueError, message):
            Greeting._extract_expiry(expiry)


class TestResult(TestCase):

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result.xml').read_bytes()
        result = Result.parse(xml, SCHEMA)
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.msg, 'Command completed successfully')
        self.assertEqual(result.res_data, None)
        self.assertEqual(result.cl_tr_id, 'sdmj001#17-03-06at18:48:03')
        self.assertEqual(result.sv_tr_id, 'ReqID-0000126633')


class TestResultExtensions(TestCase):

    TEST_EXTENSIONS = {
        DummyExtension.tag: DummyExtension,
        OtherExtension.tag: OtherExtension,
    }

    def setUp(self):
        EXTENSIONS.update(self.TEST_EXTENSIONS)

    def tearDown(self):
        for key in self.TEST_EXTENSIONS:
            del EXTENSIONS[key]

    def test_extract_none(self):
        extension = None
        result = Result._extract_extensions(extension)
        self.assertEqual(result, [])

    def test_extract_unknown(self):
        extension = EM.extension(EM.unknown())
        with LogCapture('epplib.responses.base', propagate=False) as log_handler:
            result = Result._extract_extensions(extension)

        self.assertEqual(result, [])

        message = 'Could not find class to extract extension {urn:ietf:params:xml:ns:epp-1.0}unknown.'
        log_handler.check(('epplib.responses.base', 'INFO', message))

    def test_extract(self):
        EXT = ElementMaker(namespace='dummy')
        extension = EM.extension(
            EXT.dummyExtension('Gazpacho!'),
            EXT.otherExtension(value='1'),
        )
        result = Result._extract_extensions(extension)
        self.assertEqual(result, [DummyExtension('Gazpacho!'), OtherExtension(1)])

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result_dummy_extension.xml').read_bytes()
        result = Result.parse(xml)
        self.assertEqual(result.extensions, [DummyExtension('Gazpacho!')])
