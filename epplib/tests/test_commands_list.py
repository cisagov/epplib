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

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands.list import ListContacts, ListDomains, ListKeysets, ListNssets
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestList(XMLTestCase):
    tr_id = 'abc123'

    def test_valid(self):
        self.assertRequestValid(ListContacts, {})
        self.assertRequestValid(ListDomains, {})
        self.assertRequestValid(ListKeysets, {})
        self.assertRequestValid(ListNssets, {})

    def test_data(self):
        data = (
            (ListContacts, 'listContacts'),
            (ListDomains, 'listDomains'),
            (ListKeysets, 'listKeysets'),
            (ListNssets, 'listNssets'),
        )
        for cls, tag in data:
            with self.subTest(tag=tag):
                root = fromstring(cls().xml(self.tr_id))
                fred = ElementMaker(namespace=NAMESPACE.FRED)
                expected = make_epp_root(
                    EM.extension(
                        fred.extcommand(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                            fred(tag),
                            fred.clTRID(self.tr_id),
                        )
                    )
                )
                self.assertXMLEqual(root, expected)
