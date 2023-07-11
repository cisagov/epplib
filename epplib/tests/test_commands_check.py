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

from epplib.commands import CheckContact, CheckDomain, CheckKeyset, CheckNsset
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestCheckDomain(XMLTestCase):
    domains = ["domain.cz", "other.com"]

    def test_valid(self):
        self.assertRequestValid(CheckDomain, {"names": self.domains})

    def test_data(self):
        root = fromstring(CheckDomain(self.domains).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.check(
                    domain.check(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        *[domain.name(item) for item in self.domains]
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestCheckContact(XMLTestCase):
    contacts = ["CID-MYOWN", "CID-NONE"]

    def test_valid(self):
        self.assertRequestValid(CheckContact, {"ids": self.contacts})

    def test_data(self):
        root = fromstring(CheckContact(self.contacts).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.check(
                    contact.check(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_CONTACT
                        },
                        *[contact.id(item) for item in self.contacts]
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestCheckNsset(XMLTestCase):
    nssets = ["NID-MYNSSET", "NID-NONE"]

    def test_valid(self):
        self.assertRequestValid(CheckNsset, {"ids": self.nssets})

    def test_data(self):
        root = fromstring(CheckNsset(self.nssets).xml())
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.command(
                EM.check(
                    nsset.check(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_NSSET
                        },
                        *[nsset.id(item) for item in self.nssets]
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestCheckKeyset(XMLTestCase):
    keysets = ["KID-MYKEYSET", "KID-NONE"]

    def test_valid(self):
        self.assertRequestValid(CheckKeyset, {"ids": self.keysets})

    def test_data(self):
        root = fromstring(CheckKeyset(self.keysets).xml())
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.command(
                EM.check(
                    keyset.check(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_KEYSET
                        },
                        *[keyset.id(item) for item in self.keysets]
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
