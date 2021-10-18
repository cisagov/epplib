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

from epplib.commands import DeleteContact, DeleteDomain, DeleteKeyset
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestDeleteDomain(XMLTestCase):
    domain = 'domain.cz'

    def test_valid(self):
        self.assertRequestValid(DeleteDomain, {'name': self.domain})

    def test_data(self):
        root = fromstring(DeleteDomain(self.domain).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.delete(
                    domain.delete(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.domain)
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestDeleteContact(XMLTestCase):
    contact = 'CID-MYOWN'

    def test_valid(self):
        self.assertRequestValid(DeleteContact, {'id': self.contact})

    def test_data(self):
        root = fromstring(DeleteContact(self.contact).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.delete(
                    contact.delete(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.contact)
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestDeleteKeyset(XMLTestCase):
    keyset = 'KID-MYOWN'

    def test_valid(self):
        self.assertRequestValid(DeleteKeyset, {'id': self.keyset})

    def test_data(self):
        root = fromstring(DeleteKeyset(self.keyset).xml())
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.command(
                EM.delete(
                    keyset.delete(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_KEYSET},
                        keyset.id(self.keyset)
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
