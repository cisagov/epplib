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

from epplib.models.list import ListResultData
from epplib.responses import GetResultsResult, ListResult
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestListResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_list.xml").read_bytes()
        result = ListResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, [ListResultData(4)])

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = ListResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestGetResultsResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_get_results.xml").read_bytes()
        result = GetResultsResult.parse(xml, SCHEMA)
        expected = [
            "1.1.1.7.4.5.2.2.2.0.2.4.e164.arpa",
            "mydomain.cz",
            "thisdomain.cz",
            "trdomain.cz",
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = GetResultsResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
