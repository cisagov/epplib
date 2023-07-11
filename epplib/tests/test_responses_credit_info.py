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
from decimal import Decimal
from unittest import TestCase

from epplib.models.credit_info import CreditInfoResultData
from epplib.responses import CreditInfoResult
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestCreditInfoResult(TestCase):
    def test_parse(self):
        xml = (BASE_DATA_PATH / "responses/result_credit_info.xml").read_bytes()
        result = CreditInfoResult.parse(xml, SCHEMA)
        expected = [
            CreditInfoResultData("0.2.4.e164.arpa", Decimal(66112)),
            CreditInfoResultData("cz", Decimal(82640)),
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = CreditInfoResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
