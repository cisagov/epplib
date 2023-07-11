#
# Copyright (C) 2021-2023  CZ.NIC, z. s. p. o.
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
from unittest import TestCase

from lxml.builder import ElementMaker

from epplib.constants import NAMESPACE
from epplib.models import ExtraAddr
from epplib.responses.extensions import EnumInfoExtension, MailingAddressExtension


class TestEnumInfoExtension(TestCase):
    EM = ElementMaker(namespace=NAMESPACE.NIC_ENUMVAL)

    def test_extract_empty(self):
        element = self.EM.infData()
        self.assertEqual(
            EnumInfoExtension.extract(element), EnumInfoExtension(None, None)
        )

    def test_extract(self):
        element = self.EM.infData(
            self.EM.valExDate("2018-01-02"),
            self.EM.publish("0"),
        )
        result = EnumInfoExtension.extract(element)
        expected = EnumInfoExtension(date(2018, 1, 2), False)
        self.assertEqual(result, expected)


class TestMailingAddressExtension(TestCase):
    EM = ElementMaker(namespace=NAMESPACE.NIC_EXTRA_ADDR)

    def test_extract(self):
        addr = ExtraAddr(
            street=["Dlouha 24"], city="Lysa nad Labem", pc="28922", cc="CZ"
        )
        element = self.EM.infData(self.EM.mailing(addr.get_payload()))
        result = MailingAddressExtension.extract(element)
        expected = MailingAddressExtension(addr=addr)
        self.assertEqual(result, expected)
