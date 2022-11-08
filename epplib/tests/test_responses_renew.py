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
from datetime import date
from unittest import TestCase

from epplib.models.renew import RenewDomainResultData
from epplib.responses import RenewDomainResult
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestRenewDomainResult(TestCase):

    def test_parse(self):
        template = (BASE_DATA_PATH / 'responses/result_renew_domain_template.xml').read_bytes()
        data = (
            (b'<domain:exDate>2020-07-11</domain:exDate>', date(2020, 7, 11)),
            (b'', None),
        )
        for tag, ex_date in data:
            with self.subTest(tag=tag):
                xml = template.replace(b'{ex_date}', tag)
                result = RenewDomainResult.parse(xml, SCHEMA)
                expected = [
                    RenewDomainResultData('mydomain.cz', ex_date),
                ]
                self.assertEqual(result.code, 1000)
                self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = RenewDomainResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
