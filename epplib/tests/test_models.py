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
from epplib.models import (ContactAddr, Disclose, DiscloseField, Dnskey, Ident, IdentType, Ns, Period, PostalInfo,
                           Statement, Status, Unit)
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

    def test_extract_full(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = EM.addr(
            EM.street('Street 1'),
            EM.street('Street 2'),
            EM.city('City'),
            EM.pc('12345'),
            EM.cc('cz'),
            EM.sp('Province'),
        )
        expected = ContactAddr(
            street=['Street 1', 'Street 2'],
            city='City',
            pc='12345',
            cc='cz',
            sp='Province',
        )
        self.assertEqual(ContactAddr.extract(addr), expected)

    def test_extract_minimal(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = EM.addr()
        expected = ContactAddr(
            street=[],
            city=None,
            pc=None,
            cc=None,
            sp=None,
        )
        self.assertEqual(ContactAddr.extract(addr), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = EM.disclose(
            EM.addr(),
            flag='1'
        )
        expected = Disclose(True, {DiscloseField.ADDR})
        self.assertEqual(Disclose.extract(disclose), expected)


class TestDisclose(XMLTestCase):

    def test_get_payload(self):
        data = (
            (True, '1'),
            (False, '0'),
        )
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        for flag, result in data:
            with self.subTest(flag=flag):
                disclose = Disclose(flag=flag, fields={DiscloseField.VAT, DiscloseField.EMAIL})
                expected = EM.disclose(EM.email, EM.vat, flag=result)
                self.assertXMLEqual(disclose.get_payload(), expected)


class TestDnskey(XMLTestCase):

    def test_get_payload(self):
        dnskey = Dnskey(257, 3, 5, 'AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8')
        EM = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = EM.dnskey(
            EM.flags('257'),
            EM.protocol('3'),
            EM.alg('5'),
            EM.pubKey('AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8'),
        )
        self.assertXMLEqual(dnskey.get_payload(), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        dnskey = EM.dnskey(
            EM.flags('257'),
            EM.protocol('3'),
            EM.alg('5'),
            EM.pubKey('aXN4Y2lpd2ZicWtkZHF4dnJyaHVtc3BreXN6ZGZy'),
        )
        expected = Dnskey(flags=257, protocol=3, alg=5, pub_key='aXN4Y2lpd2ZicWtkZHF4dnJyaHVtc3BreXN6ZGZy')
        self.assertEqual(Dnskey.extract(dnskey), expected)


class TestIdent(XMLTestCase):

    def test_get_payload(self):
        ident = Ident(IdentType.PASSPORT, '1234567890')
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = EM.ident('1234567890', type='passport')
        self.assertXMLEqual(ident.get_payload(), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        ident = EM.ident('12345', type='passport')
        expected = Ident(IdentType.PASSPORT, '12345')
        self.assertEqual(Ident.extract(ident), expected)


class TestNs(XMLTestCase):
    def test_get_payload(self):
        ns = Ns('ns1.domain.cz', ['217.31.207.130', '217.31.207.131'])
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = EM.ns(
            EM.name('ns1.domain.cz'),
            EM.addr('217.31.207.130'),
            EM.addr('217.31.207.131'),
        )
        self.assertXMLEqual(ns.get_payload(), expected)


class TestPeriod(XMLTestCase):
    def test_get_payload(self):
        period = Period(3, Unit.MONTH)
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = EM.period('3', unit='m')
        self.assertXMLEqual(period.get_payload(), expected)


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

    def test_extract_full(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(['Street 1'], 'City', '12345', 'CZ')
        element = EM.postalInfo(
            EM.name('John'),
            EM.org('Company Inc.'),
            addr.get_payload(),
        )
        expected = PostalInfo(name='John', addr=addr, org='Company Inc.')
        self.assertEqual(PostalInfo.extract(element), expected)

    def test_extract_minimal(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        element = EM.postalInfo()
        expected = PostalInfo(None, None, None)
        self.assertEqual(PostalInfo.extract(element), expected)


class TestStatement(XMLTestCase):

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.EPP)
        element = EM.statement(
            EM.purpose(
                EM.admin(),
                EM.prov(),
            ),
            EM.recipient(
                EM.public(),
            ),
            EM.retention(
                EM.stated(),
            ),
        )
        expected = Statement(['admin', 'prov'], ['public'], 'stated')
        self.assertEqual(Statement.extract(element), expected)


class TestStatus(XMLTestCase):

    def test_post_init(self):
        self.assertEqual(Status('ok', 'is ok', 'cs'), Status('ok', 'is ok', 'cs'))
        self.assertEqual(Status('ok', 'is ok'), Status('ok', 'is ok', 'en'))
        self.assertEqual(Status('ok', 'is ok', None), Status('ok', 'is ok', 'en'))

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        self.assertEqual(Status.extract(EM.status('It is ok.', s='ok', lang='cz')), Status('ok', 'It is ok.', 'cz'))
        self.assertEqual(Status.extract(EM.status('It is ok.', s='ok')), Status('ok', 'It is ok.', 'en'))
