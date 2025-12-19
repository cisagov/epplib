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

from lxml.builder import ElementMaker

from epplib.constants import NAMESPACE
from epplib.models import (
    AddressField,
    AddressFieldDisclose,
    ContactAddr,
    Disclose,
    DiscloseField,
    Dnskey,
    Ident,
    IdentType,
    Ns,
    Period,
    PostalInfo,
    PostalInfoType,
    Statement,
    Status,
    TestResult,
    Unit,
)
from epplib.tests.utils import XMLTestCase


class TestAddr(XMLTestCase):
    def test_get_payload_full(self):
        params = {
            "street": ["Door 42", "Street 123"],
            "city": "City",
            "pc": "12300",
            "cc": "CZ",
            "sp": "Province",
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(**params)  # type: ignore[arg-type] # dataclass annotation bug
        expected = EM.addr(
            EM.street(params["street"][0]),
            EM.street(params["street"][1]),
            EM.city(params["city"]),
            EM.sp(params["sp"]),
            EM.pc(params["pc"]),
            EM.cc(params["cc"]),
        )
        self.assertXMLEqual(addr.get_payload(), expected)

    def test_get_payload_minimal(self):
        params = {
            "street": ["Street 123"],
            "city": "City",
            "pc": "12300",
            "cc": "CZ",
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(**params)  # type: ignore[arg-type] # dataclass annotation bug
        expected = EM.addr(
            EM.street(params["street"][0]),
            EM.city(params["city"]),
            EM.pc(params["pc"]),
            EM.cc(params["cc"]),
        )
        self.assertXMLEqual(addr.get_payload(), expected)

    def test_extract_full(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = EM.addr(
            EM.street("Street 1"),
            EM.street("Street 2"),
            EM.city("City"),
            EM.pc("12345"),
            EM.cc("cz"),
            EM.sp("Province"),
        )
        expected = ContactAddr(
            street=["Street 1", "Street 2"],
            city="City",
            pc="12345",
            cc="cz",
            sp="Province",
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
        disclose = EM.disclose(EM.addr(), flag="1")
        expected = Disclose(True, {DiscloseField.ADDR})
        self.assertEqual(Disclose.extract(disclose), expected)


class TestDisclose(XMLTestCase):
    def test_get_payload(self):
        data = (
            (True, "1"),
            (False, "0"),
        )
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        for flag, result in data:
            with self.subTest(flag=flag):
                disclose = Disclose(
                    flag=flag, fields={DiscloseField.NAME, DiscloseField.ORG, DiscloseField.VAT, DiscloseField.EMAIL}
                )
                expected = EM.disclose(EM.name, EM.org, EM.email, EM.vat, flag=result)
                self.assertXMLEqual(disclose.get_payload(), expected)

    def test_get_payload_order(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = Disclose(flag=True, fields=set(DiscloseField))
        expected = EM.disclose(
            EM.name,
            EM.org,
            EM.addr,
            EM.voice,
            EM.fax,
            EM.email,
            EM.vat,
            EM.ident,
            EM.notifyEmail,
            flag="1",
        )
        self.assertXMLEqual(disclose.get_payload(), expected)

    def test_hide_street_and_postal_code(self):
        """Test explicitly hiding street and postal code with flag=False.
        When flag=False, we are telling the registry these address fields should NOT be disclosed publicly.
        """
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = Disclose(
            flag=False,
            fields={DiscloseField.NAME, DiscloseField.EMAIL},
            addr_fields=[
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.STREET),
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.PC),
            ]
        )
        expected = EM.disclose(
            EM.name,
            EM.addrField(type="loc", field="street"),
            EM.addrField(type="loc", field="pc"),
            EM.email,
            flag="0",
        )
        self.assertXMLEqual(disclose.get_payload(), expected)

    def test_disclose_city_state_country(self):
        """Test to explicitly disclose city/state/country."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = Disclose(
            flag=True,
            fields={DiscloseField.NAME, DiscloseField.EMAIL},
            addr_fields=[
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.CITY),
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.SP),
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.CC),
            ]
        )
        expected = EM.disclose(
            EM.name,
            EM.addrField(type="loc", field="city"),
            EM.addrField(type="loc", field="sp"),
            EM.addrField(type="loc", field="cc"),
            EM.email,
            flag="1",
        )
        self.assertXMLEqual(disclose.get_payload(), expected)

    def test_addr_fields_order(self):
        """Test that addr_fields are output after standard fields and in the order provided."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = Disclose(
            flag=False,
            fields={DiscloseField.NAME, DiscloseField.ADDR, DiscloseField.VOICE, DiscloseField.EMAIL},
            addr_fields=[
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.PC),
                AddressFieldDisclose(PostalInfoType.INT, AddressField.STREET),
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.CITY),
                AddressFieldDisclose(PostalInfoType.INT, AddressField.CC),
            ]
        )
        # Expected: standard fields first (in enum order), then addrField elements (in provided order)
        expected = EM.disclose(
            EM.name,
            EM.addr,
            EM.addrField(type="loc", field="pc"),
            EM.addrField(type="int", field="street"),
            EM.addrField(type="loc", field="city"),
            EM.addrField(type="int", field="cc"),
            EM.voice,
            EM.email,
            flag="0",
        )
        self.assertXMLEqual(disclose.get_payload(), expected)

    def test_extract_with_addr_fields(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        # Test with flag=0 (do not disclose)
        disclose_elem_hidden = EM.disclose(
            EM.email,
            EM.addrField(type="loc", field="street"),
            EM.addrField(type="int", field="pc"),
            flag="0",
        )
        result_hidden = Disclose.extract(disclose_elem_hidden)

        self.assertFalse(result_hidden.flag)
        self.assertEqual(result_hidden.fields, {DiscloseField.EMAIL})
        self.assertEqual(len(result_hidden.addr_fields), 2)
        self.assertEqual(result_hidden.addr_fields[0].type, PostalInfoType.LOC)
        self.assertEqual(result_hidden.addr_fields[0].field, AddressField.STREET)
        self.assertEqual(result_hidden.addr_fields[1].type, PostalInfoType.INT)
        self.assertEqual(result_hidden.addr_fields[1].field, AddressField.PC)

        # Test with flag=1 (disclose)
        disclose_elem = EM.disclose(
            EM.name,
            EM.addrField(type="loc", field="city"),
            EM.addrField(type="loc", field="cc"),
            flag="1",
        )
        result = Disclose.extract(disclose_elem)

        self.assertTrue(result.flag)
        self.assertEqual(result.fields, {DiscloseField.NAME})
        self.assertEqual(len(result.addr_fields), 2)
        self.assertEqual(result.addr_fields[0].type, PostalInfoType.LOC)
        self.assertEqual(result.addr_fields[0].field, AddressField.CITY)
        self.assertEqual(result.addr_fields[1].type, PostalInfoType.LOC)
        self.assertEqual(result.addr_fields[1].field, AddressField.CC)

    def test_infupd_disclose_type(self):
        """Test infupdDiscloseType with addrField."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose = Disclose(
            flag=True,
            fields={DiscloseField.EMAIL},
            addr_fields=[
                AddressFieldDisclose(PostalInfoType.LOC, AddressField.CITY),
            ]
        )

        expected = EM.disclose(
            EM.addrField(type="loc", field="city"),
            EM.email,
            flag="1",
        )
        self.assertXMLEqual(disclose.get_payload(), expected)

        disclose_elem = EM.disclose(
            EM.email,
            EM.addrField(type="loc", field="city"),
            flag="1",
        )
        result = Disclose.extract(disclose_elem)
        self.assertTrue(result.flag)
        self.assertEqual(result.fields, {DiscloseField.EMAIL})
        self.assertEqual(len(result.addr_fields), 1)
        self.assertEqual(result.addr_fields[0].type, PostalInfoType.LOC)
        self.assertEqual(result.addr_fields[0].field, AddressField.CITY)


class TestAddressFieldDisclose(XMLTestCase):
    def test_get_payload(self):
        """Test basic XML generation for address field disclosure."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr_field = AddressFieldDisclose(PostalInfoType.LOC, AddressField.CITY)
        expected = EM.addrField(type="loc", field="city")
        self.assertXMLEqual(addr_field.get_payload(), expected)

    def test_extract(self):
        """Test basic XML parsing for address field disclosure."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr_field_elem = EM.addrField(type="int", field="cc")
        result = AddressFieldDisclose.extract(addr_field_elem)

        self.assertEqual(result.type, PostalInfoType.INT)
        self.assertEqual(result.field, AddressField.CC)

    def test_roundtrip(self):
        """Test that extraction and generation are consistent."""
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        original = EM.addrField(type="loc", field="sp")

        extracted = AddressFieldDisclose.extract(original)
        generated = extracted.get_payload()
        re_extracted = AddressFieldDisclose.extract(generated)

        self.assertEqual(extracted, re_extracted)


class TestDnskey(XMLTestCase):
    def test_get_payload(self):
        dnskey = Dnskey(
            257, 3, 5, "AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8"
        )
        EM = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = EM.dnskey(
            EM.flags("257"),
            EM.protocol("3"),
            EM.alg("5"),
            EM.pubKey("AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8"),
        )
        self.assertXMLEqual(dnskey.get_payload(), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        dnskey = EM.dnskey(
            EM.flags("257"),
            EM.protocol("3"),
            EM.alg("5"),
            EM.pubKey("aXN4Y2lpd2ZicWtkZHF4dnJyaHVtc3BreXN6ZGZy"),
        )
        expected = Dnskey(
            flags=257,
            protocol=3,
            alg=5,
            pub_key="aXN4Y2lpd2ZicWtkZHF4dnJyaHVtc3BreXN6ZGZy",
        )
        self.assertEqual(Dnskey.extract(dnskey), expected)


class TestIdent(XMLTestCase):
    def test_get_payload(self):
        ident = Ident(IdentType.PASSPORT, "1234567890")
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = EM.ident("1234567890", type="passport")
        self.assertXMLEqual(ident.get_payload(), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        ident = EM.ident("12345", type="passport")
        expected = Ident(IdentType.PASSPORT, "12345")
        self.assertEqual(Ident.extract(ident), expected)


class TestNs(XMLTestCase):
    def test_get_payload(self):
        ns = Ns("ns1.domain.cz", ["217.31.207.130", "217.31.207.131"])
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = EM.ns(
            EM.name("ns1.domain.cz"),
            EM.addr("217.31.207.130"),
            EM.addr("217.31.207.131"),
        )
        self.assertXMLEqual(ns.get_payload(), expected)

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        ns = EM.ns(
            EM.name("mydomain.cz"),
            EM.addr("111.222.111.222"),
            EM.addr("111.222.111.333"),
        )
        expected = Ns(name="mydomain.cz", addrs=["111.222.111.222", "111.222.111.333"])
        self.assertEqual(Ns.extract(ns), expected)


class TestPeriod(XMLTestCase):
    def test_get_payload(self):
        period = Period(3, Unit.MONTH)
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = EM.period("3", unit="m")
        self.assertXMLEqual(period.get_payload(), expected)


class TestPostalInfo(XMLTestCase):
    addr = ContactAddr(street=["Street 123"], city="City", pc="12300", cc="CZ")

    def test_get_payload(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        data = (
            # postal_info, expected
            (PostalInfo(), EM.postalInfo()),
            (PostalInfo("John"), EM.postalInfo(EM.name("John"))),
            (PostalInfo(addr=self.addr), EM.postalInfo(self.addr.get_payload())),
            (PostalInfo(org="JMC"), EM.postalInfo(EM.org("JMC"))),
            (PostalInfo(org=""), EM.postalInfo(EM.org(""))),
            (
                PostalInfo("John", self.addr, "JMC"),
                EM.postalInfo(EM.name("John"), EM.org("JMC"), self.addr.get_payload()),
            ),
        )
        for postal_info, expected in data:
            with self.subTest(postal_info=postal_info):
                self.assertXMLEqual(postal_info.get_payload(), expected)

    def test_extract_full(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        addr = ContactAddr(["Street 1"], "City", "12345", "CZ")
        element = EM.postalInfo(
            EM.name("John"),
            EM.org("Company Inc."),
            addr.get_payload(),
        )
        expected = PostalInfo(name="John", addr=addr, org="Company Inc.")
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
        expected = Statement(["admin", "prov"], ["public"], "stated")
        self.assertEqual(Statement.extract(element), expected)


class TestStatus(XMLTestCase):
    def test_post_init(self):
        self.assertEqual(Status("ok", "is ok", "cs"), Status("ok", "is ok", "cs"))
        self.assertEqual(Status("ok", "is ok"), Status("ok", "is ok", "en"))
        self.assertEqual(Status("ok", "is ok", None), Status("ok", "is ok", "en"))

    def test_extract(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        self.assertEqual(
            Status.extract(EM.status("It is ok.", s="ok", lang="cz")),
            Status("ok", "It is ok.", "cz"),
        )
        self.assertEqual(
            Status.extract(EM.status("It is ok.", s="ok")),
            Status("ok", "It is ok.", "en"),
        )


class TestTestResult(XMLTestCase):
    def test_extract_full(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        element = EM.result(
            EM.testname("glue_ok"),
            EM.status("true"),
            EM.note("This is a note."),
        )
        expected = TestResult(testname="glue_ok", status=True, note="This is a note.")
        self.assertEqual(TestResult.extract(element), expected)

    def test_extract_minimal(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        element = EM.result(
            EM.testname("glue_ok"),
            EM.status("false"),
        )
        expected = TestResult(testname="glue_ok", status=False, note=None)
        self.assertEqual(TestResult.extract(element), expected)
