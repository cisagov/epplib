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

from datetime import date, datetime, timedelta, timezone
from typing import cast
from unittest import TestCase

from epplib.responses import InfoDomainResult
from epplib.responses.info import Status
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestInfoDomainResult(TestCase):

    def test_parse_minimal(self):
        xml = (BASE_DATA_PATH / 'responses/result_info_domain_minimal.xml').read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResult.Domain(
                name='mydomain.cz',
                roid='D0009907597-CZ',
                statuses=[Status('ok', 'Object is without restrictions', 'en')],
                cl_id='REG-MYREG',
                registrant='CID-MYOWN',
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(cast(InfoDomainResult, result).data, expected)

    def test_parse_full(self):
        xml = (BASE_DATA_PATH / 'responses/result_info_domain.xml').read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResult.Domain(
                name='mydomain.cz',
                roid='D0009907597-CZ',
                statuses=[Status('ok', 'Object is without restrictions', 'en')],
                cl_id='REG-MYREG',
                registrant='CID-MYOWN',
                admins=['CID-ADMIN2', 'CID-ADMIN3'],
                nsset='NID-MYNSSET',
                keyset='KID-MYKEYSET',
                cr_id='REG-MYREG',
                cr_date=datetime(2017, 7, 11, 13, 28, 48, tzinfo=timezone(timedelta(hours=2))),
                up_id='REG-MYREG',
                up_date=datetime(2017, 7, 18, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))),
                ex_date=date(2020, 7, 11),
                tr_date=datetime(2017, 7, 19, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))),
                auth_info='rvBcaTVq',
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(cast(InfoDomainResult, result).data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / 'responses/result_error.xml').read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)

    def test_status(self):
        self.assertEqual(Status('ok', 'is ok', 'cs'), Status('ok', 'is ok', 'cs'))
        self.assertEqual(Status('ok', 'is ok'), Status('ok', 'is ok', 'en'))
        self.assertEqual(Status('ok', 'is ok', None), Status('ok', 'is ok', 'en'))
