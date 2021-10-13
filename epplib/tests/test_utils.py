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

from datetime import date
from typing import cast
from unittest import TestCase

from dateutil.relativedelta import relativedelta
from lxml.etree import Element, QName

from epplib.tests.utils import EM
from epplib.utils import ParseXMLMixin, safe_parse


class TestSafeParse(TestCase):

    def test_parse(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <simple xmlns="http://www.nic.cz/xml/epp"/>'''
        element = safe_parse(data)
        self.assertEqual(element.tag, QName('http://www.nic.cz/xml/epp', 'simple'))

    def test_exception_on_doctype(self):
        data = b'''<?xml version="1.0" encoding="UTF-8"?>
                   <!DOCTYPE simple>
                   <simple/>'''
        with self.assertRaisesRegex(ValueError, 'Doctype is not allowed\\.'):
            safe_parse(data)


class TestParseXMLMixin(TestCase):
    def test_find(self):
        element = EM.svcMenu(EM.lang('en'), EM.lang('cs'))
        self.assertEqual(cast(Element, ParseXMLMixin._find(element, './epp:lang')).text, 'en')
        self.assertEqual(ParseXMLMixin._find(element, './epp:missing'), None)

    def test_find_all(self):
        element = EM.svcMenu(EM.lang('en'), EM.lang('cs'), EM.version())
        self.assertEqual([item.text for item in ParseXMLMixin._find_all(element, './epp:lang')], ['en', 'cs'])
        self.assertEqual([item.text for item in ParseXMLMixin._find_all(element, './epp:version')], [None])
        self.assertEqual([item.text for item in ParseXMLMixin._find_all(element, './epp:missing')], [])

    def test_find_text(self):
        element = EM.svcMenu(EM.lang('en'), EM.version())
        self.assertEqual(ParseXMLMixin._find_text(element, './epp:lang'), 'en')
        self.assertEqual(ParseXMLMixin._find_text(element, './epp:version'), '')
        self.assertIsNone(ParseXMLMixin._find_text(element, './epp:missing'))

    def test_find_all_text(self):
        element = EM.svcMenu(EM.lang('en'), EM.lang('cs'), EM.version())
        self.assertEqual(ParseXMLMixin._find_all_text(element, './epp:lang'), ['en', 'cs'])
        self.assertEqual(ParseXMLMixin._find_all_text(element, './epp:version'), [''])
        self.assertEqual(ParseXMLMixin._find_all_text(element, './epp:missing'), [])

    def test_find_attrib(self):
        element = EM.response(EM.result(code='1000'))
        self.assertEqual(ParseXMLMixin._find_attrib(element, './epp:result', 'code'), '1000')
        self.assertEqual(ParseXMLMixin._find_attrib(element, './epp:result', 'other'), None)
        self.assertEqual(ParseXMLMixin._find_attrib(element, './epp:other', 'code'), None)

    def test_find_child(self):
        element = EM.statement(EM.purpose(EM.admin()))
        self.assertEqual(ParseXMLMixin._find_child(element, './epp:purpose'), 'admin')
        self.assertEqual(ParseXMLMixin._find_child(element, './epp:recipient'), None)

    def test_find_children(self):
        element = EM.statement(EM.purpose(EM.admin(), EM.prov()))
        self.assertEqual(ParseXMLMixin._find_children(element, './epp:purpose'), ['admin', 'prov'])
        self.assertEqual(ParseXMLMixin._find_children(element, './epp:recipient'), [])

    def test_optional(self):
        self.assertEqual(ParseXMLMixin._optional(int, '1'), 1)
        self.assertEqual(ParseXMLMixin._optional(int, None), None)

    def test_parse_date(self):
        self.assertEqual(ParseXMLMixin._parse_date('2021-07-21'), date(2021, 7, 21))

    def test_parse_duration_valid(self):
        data = (
            ('P1Y', relativedelta(years=1)),
            ('P2M', relativedelta(months=2)),
            ('P3D', relativedelta(days=3)),
            ('PT4H', relativedelta(hours=4)),
            ('PT5M', relativedelta(minutes=5)),
            ('PT6S', relativedelta(seconds=6)),
            ('PT6.5S', relativedelta(seconds=6, microseconds=500000)),
            ('PT6.05S', relativedelta(seconds=6, microseconds=50000)),
            ('P2MT5M', relativedelta(months=2, minutes=5)),
            ('P1Y2M3DT4H5M6S', relativedelta(years=1, months=2, days=3, hours=4, minutes=5, seconds=6)),
            ('-P1Y', relativedelta(years=-1)),
            ('-P1YT2H', relativedelta(years=-1, hours=-2)),
        )
        for item, expected in data:
            with self.subTest(item=item):
                self.assertEqual(ParseXMLMixin._parse_duration(item), expected)

    def test_parse_duration_invalid(self):
        data = (
            'invalid',
            'PY',
            'P1.5Y',
            'P1Z',
            'PT1Z',
            'P2M5M',
            'P2M5H',
            '1Y',
        )
        message = 'Can not parse string "{}" as duration\\.'
        for item in data:
            with self.subTest(item=item):
                with self.assertRaisesRegex(ValueError, message.format(item)):
                    ParseXMLMixin._parse_duration(item)

    def test_str_to_bool(self):
        self.assertEqual(ParseXMLMixin._str_to_bool(None), None)
        self.assertEqual(ParseXMLMixin._str_to_bool('1'), True)
        self.assertEqual(ParseXMLMixin._str_to_bool('0'), False)
        self.assertEqual(ParseXMLMixin._str_to_bool('true'), True)
        self.assertEqual(ParseXMLMixin._str_to_bool('false'), False)
        with self.assertRaisesRegex(ValueError, 'Value "other" is not in the list of known boolean values\\.'):
            ParseXMLMixin._str_to_bool('other')
