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

from decimal import Decimal
from unittest import TestCase

from lxml.builder import ElementMaker

from epplib.constants import NAMESPACE
from epplib.responses.poll_messages import LowCredit


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
