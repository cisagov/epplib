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

from epplib.commands.list import (ListContacts, ListDomains, ListDomainsByContact, ListDomainsByKeyset,
                                  ListDomainsByNsset, ListKeysets, ListKeysetsByContact, ListNssets,
                                  ListNssetsByContact, ListNssetsByNs)
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestList(XMLTestCase):

    def test_valid(self):
        self.assertRequestValid(ListContacts, {})
        self.assertRequestValid(ListDomains, {})
        self.assertRequestValid(ListKeysets, {})
        self.assertRequestValid(ListNssets, {})

    def test_data(self):
        tr_id = 'abc123'
        data = (
            (ListContacts, 'listContacts'),
            (ListDomains, 'listDomains'),
            (ListKeysets, 'listKeysets'),
            (ListNssets, 'listNssets'),
        )
        for cls, tag in data:
            with self.subTest(tag=tag):
                root = fromstring(cls().xml(tr_id))
                fred = ElementMaker(namespace=NAMESPACE.FRED)
                expected = make_epp_root(
                    EM.extension(
                        fred.extcommand(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                            fred(tag),
                            fred.clTRID(tr_id),
                        )
                    )
                )
                self.assertXMLEqual(root, expected)


class TestListBy(XMLTestCase):

    def test_valid(self):
        self.assertRequestValid(ListDomainsByContact, {'id': 'item_id'})
        self.assertRequestValid(ListDomainsByNsset, {'id': 'item_id'})
        self.assertRequestValid(ListDomainsByKeyset, {'id': 'item_id'})
        self.assertRequestValid(ListDomainsByContact, {'id': 'item_id'})
        self.assertRequestValid(ListKeysetsByContact, {'id': 'item_id'})
        self.assertRequestValid(ListNssetsByContact, {'id': 'item_id'})
        self.assertRequestValid(ListNssetsByNs, {'name': 'item_id'})

    def test_data(self):
        tr_id = 'abc123'
        data = (
            (ListDomainsByContact, 'domainsByContact', 'id'),
            (ListDomainsByNsset, 'domainsByNsset', 'id'),
            (ListDomainsByKeyset, 'domainsByKeyset', 'id'),
            (ListDomainsByContact, 'domainsByContact', 'id'),
            (ListKeysetsByContact, 'keysetsByContact', 'id'),
            (ListNssetsByNs, 'nssetsByNs', 'name'),
        )
        for cls, command_tag, item_tag in data:
            with self.subTest(tag=command_tag):
                root = fromstring(cls('item_id').xml(tr_id))
                fred = ElementMaker(namespace=NAMESPACE.FRED)
                expected = make_epp_root(
                    EM.extension(
                        fred.extcommand(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                            fred(command_tag, fred(item_tag, 'item_id')),
                            fred.clTRID(tr_id),
                        )
                    )
                )
                self.assertXMLEqual(root, expected)
