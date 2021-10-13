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

from epplib.constants import NAMESPACE
from epplib.models import ContactAddr, Disclose, DiscloseFields, Ident, IdentType, PostalInfo, Status
from epplib.tests.utils import XMLTestCase


class TestAddr(XMLTestCase):

    def test_get_payload_full(self):
        params = {
            'street': ['Door 42', 'Street 123'],
            'city': 'City',
            'pc': '12300',
            'cc': 'CZ',
            'sp': 'Province'
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(**params)  # type: ignore
        expected = EM.addr(
            EM.street(params['street'][0]),
            EM.street(params['street'][1]),
            EM.city(params['city']),
            EM.sp(params['sp']),
            EM.pc(params['pc']),
            EM.cc(params['cc']),
        )
        self.assertXMLEqual(addr.get_payload(), expected)

    def test_get_payload_minimal(self):
        params = {
            'street': ['Street 123'],
            'city': 'City',
            'pc': '12300',
            'cc': 'CZ',
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(**params)  # type: ignore
        expected = EM.addr(
            EM.street(params['street'][0]),
            EM.city(params['city']),
            EM.pc(params['pc']),
            EM.cc(params['cc']),
        )
        self.assertXMLEqual(addr.get_payload(), expected)


class TestDisclose(XMLTestCase):

    def test_get_payload(self):
        data = (
            (True, '1'),
            (False, '0'),
        )
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        for flag, result in data:
            with self.subTest(flag=flag):
                disclose = Disclose(flag=flag, fields={DiscloseFields.VAT, DiscloseFields.EMAIL})
                expected = EM.disclose(EM.email, EM.vat, flag=result)
                self.assertXMLEqual(disclose.get_payload(), expected)


class TestIdent(XMLTestCase):

    def test_get_payload(self):
        ident = Ident(IdentType.PASSPORT, '1234567890')
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = EM.ident('1234567890', type='passport')
        self.assertXMLEqual(ident.get_payload(), expected)


class TestPostalInfo(XMLTestCase):

    addr = ContactAddr(street=['Street 123'], city='City', pc='12300', cc='CZ')

    def test_get_payload_minimal(self):
        postal_info = PostalInfo('John', self.addr)
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = EM.postalInfo(
            EM.name('John'),
            self.addr.get_payload(),
        )
        self.assertXMLEqual(postal_info.get_payload(), expected)

    def test_get_payload_full(self):
        postal_info = PostalInfo('John', self.addr, 'Company Inc.')
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = EM.postalInfo(
            EM.name('John'),
            EM.org('Company Inc.'),
            self.addr.get_payload(),
        )
        self.assertXMLEqual(postal_info.get_payload(), expected)


class TestStatus(XMLTestCase):

    def test_post_init(self):
        self.assertEqual(Status('ok', 'is ok', 'cs'), Status('ok', 'is ok', 'cs'))
        self.assertEqual(Status('ok', 'is ok'), Status('ok', 'is ok', 'en'))
        self.assertEqual(Status('ok', 'is ok', None), Status('ok', 'is ok', 'en'))
