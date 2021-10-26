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

from epplib.commands import TransferContact, TransferDomain, TransferKeyset, TransferNsset
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestTransferDomain(XMLTestCase):
    params = {'name': 'trdomain.cz', 'auth_info': 'trpwd'}

    def test_valid(self):
        self.assertRequestValid(TransferDomain, self.params)

    def test_data(self):
        root = fromstring(TransferDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.transfer(
                    domain.transfer(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                        domain.authInfo(self.params['auth_info']),
                    ),
                    op='request',
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestTransferContact(XMLTestCase):
    params = {'id': 'CID-TRCONT', 'auth_info': 'trpwd'}

    def test_valid(self):
        self.assertRequestValid(TransferContact, self.params)

    def test_data(self):
        root = fromstring(TransferContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.transfer(
                    contact.transfer(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params['id']),
                        contact.authInfo(self.params['auth_info']),
                    ),
                    op='request',
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestTransferKeyset(XMLTestCase):
    params = {'id': 'KID-TRKEYSET', 'auth_info': 'trpwd'}

    def test_valid(self):
        self.assertRequestValid(TransferKeyset, self.params)

    def test_data(self):
        root = fromstring(TransferKeyset(**self.params).xml())
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.command(
                EM.transfer(
                    keyset.transfer(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_KEYSET},
                        keyset.id(self.params['id']),
                        keyset.authInfo(self.params['auth_info']),
                    ),
                    op='request',
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestTransferNsset(XMLTestCase):
    params = {'id': 'NID-TRNSSET', 'auth_info': 'trpwd'}

    def test_valid(self):
        self.assertRequestValid(TransferNsset, self.params)

    def test_data(self):
        root = fromstring(TransferNsset(**self.params).xml())
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.command(
                EM.transfer(
                    nsset.transfer(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_NSSET},
                        nsset.id(self.params['id']),
                        nsset.authInfo(self.params['auth_info']),
                    ),
                    op='request',
                )
            )
        )
        self.assertXMLEqual(root, expected)
