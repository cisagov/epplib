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
from unittest import TestCase

from epplib.models.check import (CheckContactResultData, CheckDomainResultData, CheckKeysetResultData,
                                 CheckNssetResultData)
from epplib.responses import CheckContactResult, CheckDomainResult, CheckKeysetResult, CheckNssetResult
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestCheckDomainResult(TestCase):

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result_check_domain.xml').read_bytes()
        result = CheckDomainResult.parse(xml, SCHEMA)
        expected = [
            CheckDomainResultData('mydomain.cz', True),
            CheckDomainResultData('somedomain.cz', False, 'already registered.'),
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = CheckDomainResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestCheckContactResult(TestCase):

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result_check_contact.xml').read_bytes()
        result = CheckContactResult.parse(xml, SCHEMA)
        expected = [
            CheckContactResultData('CID-MYOWN', False, 'already registered.'),
            CheckContactResultData('CID-NONE', True),
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = CheckContactResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestResultCheckNsset(TestCase):

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result_check_nsset.xml').read_bytes()
        result = CheckNssetResult.parse(xml, SCHEMA)
        expected = [
            CheckNssetResultData('NID-MYNSSET', False, 'already registered.'),
            CheckNssetResultData('NID-NONE', True),
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = CheckNssetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestResultCheckKeyset(TestCase):

    def test_parse(self):
        xml = (BASE_DATA_PATH / 'responses/result_check_keyset.xml').read_bytes()
        result = CheckKeysetResult.parse(xml, SCHEMA)
        expected = [
            CheckKeysetResultData('KID-MYKEYSET', False, 'already registered.'),
            CheckKeysetResultData('KID-NONE', True),
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = CheckKeysetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
