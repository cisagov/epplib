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
from decimal import Decimal
from unittest import TestCase

from lxml.builder import ElementMaker

from epplib.constants import NAMESPACE
from epplib.responses.poll_messages import DelData, DnsOutageData, ExpData, ImpendingExpData, LowCredit, RequestUsage


class TestPollMessages(TestCase):

    def test_low_credit(self):
        EM = ElementMaker(namespace=NAMESPACE.FRED)
        data = EM.lowCreditData(
            EM.zone('cz'),
            EM.limit(
                EM.zone('ab'),
                EM.credit('5000.00'),
            ),
            EM.credit(
                EM.zone('cd'),
                EM.credit('4999.00'),
            ),
        )
        result = LowCredit.extract(data)
        self.assertEqual(
            result,
            LowCredit(zone='cz', credit_zone='cd', credit=Decimal(4999), limit_zone='ab', limit=Decimal(5000))
        )

    def test_request_usage(self):
        EM = ElementMaker(namespace=NAMESPACE.FRED)
        data = EM.requestFeeInfoData(
            EM.periodFrom('2017-07-01T00:00:00+02:00'),
            EM.periodTo('2017-07-26T23:59:59+02:00'),
            EM.totalFreeCount('25000'),
            EM.usedCount('243'),
            EM.price('1.00'),
        )
        result = RequestUsage.extract(data)
        expected = RequestUsage(
            period_from=datetime(2017, 7, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=2))),
            period_to=datetime(2017, 7, 26, 23, 59, 59, tzinfo=timezone(timedelta(hours=2))),
            total_free_count=25000,
            used_count=243,
            price=Decimal(1),
        )
        self.assertEqual(result, expected)

    def test_domain_expiration(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        classes = (
            (ImpendingExpData, 'impendingExpData'),
            (ExpData, 'expData'),
            (DnsOutageData, 'dnsOutageData'),
            (DelData, 'delData'),
        )
        for cls, tag in classes:
            with self.subTest(tag=tag):
                data = EM(
                    tag,
                    EM.name('somedomain.cz'),
                    EM.exDate('2017-08-26'),
                )
                result = cls.extract(data)
                expected = cls(name='somedomain.cz', ex_date=date(2017, 8, 26))
                self.assertEqual(result, expected)
