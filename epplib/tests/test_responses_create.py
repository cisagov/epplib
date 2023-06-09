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
#
from datetime import date, datetime, timedelta, timezone
from unittest import TestCase

from epplib.models.create import (
    CreateContactResultData,
    CreateDomainResultData,
    CreateKeysetResultData,
    CreateNssetResultData,
)
from epplib.responses import (
    CreateContactResult,
    CreateDomainResult,
    CreateKeysetResult,
    CreateNssetResult,
)
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestCreateDomainResult(TestCase):
    def test_parse_full(self):
        xml_template = (
            BASE_DATA_PATH / "responses/result_create_domain_template.xml"
        ).read_bytes()
        xml = xml_template.replace(
            b"{exDate}", b"<domain:exDate>2018-08-09</domain:exDate>"
        )
        result = CreateDomainResult.parse(xml, SCHEMA)
        expected = [
            CreateDomainResultData(
                "thisdomain.cz",
                datetime(2017, 8, 9, 12, 31, 49, tzinfo=timezone(timedelta(hours=2))),
                date(2018, 8, 9),
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_minimal(self):
        xml_template = (
            BASE_DATA_PATH / "responses/result_create_domain_template.xml"
        ).read_bytes()
        xml = xml_template.replace(b"{exDate}", b"")
        result = CreateDomainResult.parse(xml, SCHEMA)
        expected = [
            CreateDomainResultData(
                "thisdomain.cz",
                datetime(2017, 8, 9, 12, 31, 49, tzinfo=timezone(timedelta(hours=2))),
                None,
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = CreateDomainResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestCreateContactResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_create_contact.xml").read_bytes()
        result = CreateContactResult.parse(xml, SCHEMA)
        expected = [
            CreateContactResultData(
                "CID-MYCONTACT",
                datetime(2017, 7, 28, 12, 11, 43, tzinfo=timezone(timedelta(hours=2))),
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = CreateContactResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestCreateNssetResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_create_nsset.xml").read_bytes()
        result = CreateNssetResult.parse(xml, SCHEMA)
        expected = [
            CreateNssetResultData(
                "NID-ANSSET",
                datetime(2017, 8, 9, 15, 53, 15, tzinfo=timezone(timedelta(hours=2))),
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = CreateNssetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestCreateKeysetResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_create_keyset.xml").read_bytes()
        result = CreateKeysetResult.parse(xml, SCHEMA)
        expected = [
            CreateKeysetResultData(
                "KID-AKEYSET",
                datetime(2017, 8, 9, 15, 53, 15, tzinfo=timezone(timedelta(hours=2))),
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = CreateKeysetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
