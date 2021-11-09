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

from epplib.commands import InfoContact, InfoDomain, InfoKeyset, InfoNsset
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestInfoDomain(XMLTestCase):
    params = {'name': 'thisdomain.cz'}

    def test_valid(self):
        self.assertRequestValid(InfoDomain, self.params)

    def test_data(self):
        root = fromstring(InfoDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    domain.info(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestInfoContact(XMLTestCase):
    params = {'id': 'CID-MYCONTACT'}

    def test_valid(self):
        self.assertRequestValid(InfoContact, self.params)

    def test_data(self):
        root = fromstring(InfoContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    contact.info(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params['id']),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestInfoKeyset(XMLTestCase):
    params = {'id': 'KID-MYKEYSET'}

    def test_valid(self):
        self.assertRequestValid(InfoKeyset, self.params)

    def test_data(self):
        root = fromstring(InfoKeyset(**self.params).xml())
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    keyset.info(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_KEYSET},
                        keyset.id(self.params['id']),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestInfoNsset(XMLTestCase):
    params = {'id': 'NID-MYNSSET'}

    def test_valid(self):
        self.assertRequestValid(InfoNsset, self.params)

    def test_data(self):
        root = fromstring(InfoNsset(**self.params).xml())
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    nsset.info(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_NSSET},
                        nsset.id(self.params['id']),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
