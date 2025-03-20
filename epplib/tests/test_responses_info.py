#
# Copyright (C) 2021-2022  CZ.NIC, z. s. p. o.
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
#
from datetime import date, datetime, timedelta, timezone
from unittest import TestCase

from epplib.models import (
    ContactAddr,
    Disclose,
    DiscloseField,
    Dnskey,
    Ident,
    IdentType,
    Ns,
    PostalInfo,
    Status,
)
from epplib.models.info import (
    InfoContactResultData,
    InfoDomainResultData,
    InfoKeysetResultData,
    InfoNssetResultData,
)
from epplib.responses import (
    InfoContactResult,
    InfoDomainResult,
    InfoKeysetResult,
    InfoNssetResult,
)
from epplib.tests.utils import BASE_DATA_PATH, SCHEMA


class TestInfoDomainResult(TestCase):
    def test_parse_minimal(self):
        xml = (BASE_DATA_PATH / "responses/result_info_domain_minimal.xml").read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResultData(
                name="mydomain.cz",
                roid="D0009907597-CZ",
                statuses=[Status("ok", "Object is without restrictions", "en")],
                cl_id="REG-MYREG",
                registrant="CID-MYOWN",
                admins=[],
                nsset=None,
                keyset=None,
                cr_id=None,
                cr_date=None,
                up_id=None,
                up_date=None,
                ex_date=None,
                tr_date=None,
                auth_info=None,
            )
        ]
        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_full(self):
        xml = (BASE_DATA_PATH / "responses/result_info_domain.xml").read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResultData(
                name="mydomain.cz",
                roid="D0009907597-CZ",
                statuses=[Status("ok", "Object is without restrictions", "en")],
                cl_id="REG-MYREG",
                registrant="CID-MYOWN",
                admins=["CID-ADMIN2", "CID-ADMIN3"],
                nsset="NID-MYNSSET",
                keyset="KID-MYKEYSET",
                cr_id="REG-MYREG",
                cr_date=datetime(
                    2017, 7, 11, 13, 28, 48, tzinfo=timezone(timedelta(hours=2))
                ),
                up_id="REG-MYREG",
                up_date=datetime(
                    2017, 7, 18, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))
                ),
                ex_date=date(2020, 7, 11),
                tr_date=datetime(
                    2017, 7, 19, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))
                ),
                auth_info="rvBcaTVq",
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestInfoContactResult(TestCase):
    def test_parse_full(self):
        xml = (BASE_DATA_PATH / "responses/result_info_contact.xml").read_bytes()
        result = InfoContactResult.parse(xml, SCHEMA)
        expected = [
            InfoContactResultData(
                roid="C0009746170-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-CLID",
                cr_id="REG-CRID",
                cr_date=datetime(
                    2017, 5, 4, 11, 30, 25, tzinfo=timezone(timedelta(hours=2))
                ),
                up_id="REG-UPID",
                up_date=datetime(
                    2017, 5, 5, 11, 30, 25, tzinfo=timezone(timedelta(hours=2))
                ),
                tr_date=datetime(
                    2017, 5, 6, 11, 30, 25, tzinfo=timezone(timedelta(hours=2))
                ),
                auth_info="PfLyxPC4",
                id="CID-MYCONTACT",
                postal_info=PostalInfo(
                    "Name Surname", ContactAddr(["Street"], "City", "12345", "CZ")
                ),
                voice="+420.12345",
                fax="+420.23456",
                email="email@example.com",
                disclose=Disclose(True, {DiscloseField.NAME, DiscloseField.ADDR}),
                vat="34567",
                ident=Ident(IdentType.PASSPORT, "45678"),
                notify_email="notify@example.com",
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_minimal(self):
        xml = (
            BASE_DATA_PATH / "responses/result_info_contact_minimal.xml"
        ).read_bytes()
        result = InfoContactResult.parse(xml, SCHEMA)
        expected = [
            InfoContactResultData(
                roid="C0009746170-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-CLID",
                cr_id="REG-CRID",
                cr_date=datetime(
                    2017, 5, 4, 11, 30, 25, tzinfo=timezone(timedelta(hours=2))
                ),
                up_id=None,
                up_date=None,
                tr_date=None,
                auth_info=None,
                id="CID-MYCONTACT",
                postal_info=PostalInfo(None, None),
                voice=None,
                fax=None,
                email=None,
                disclose=None,
                vat=None,
                ident=None,
                notify_email=None,
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = InfoContactResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestInfoKeysetResult(TestCase):
    def test_parse_full(self):
        xml = (BASE_DATA_PATH / "responses/result_info_keyset.xml").read_bytes()
        result = InfoKeysetResult.parse(xml, SCHEMA)
        expected = [
            InfoKeysetResultData(
                roid="K0009907596-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-MYREG",
                cr_id=None,
                cr_date=None,
                up_id=None,
                up_date=None,
                tr_date=None,
                auth_info=None,
                id="KID-MYKEYSET",
                dnskeys=[
                    Dnskey(
                        flags=257,
                        protocol=3,
                        alg=5,
                        pub_key="aXN4Y2lpd2ZicWtkZHF4dnJyaHVtc3BreXN6ZGZy",
                    ),
                    Dnskey(
                        flags=257,
                        protocol=3,
                        alg=5,
                        pub_key="eGVmbmZrY3lvcXFwamJ6aGt2YXhteXdkc2tjeXBp",
                    ),
                ],
                techs=["CID-TECH2", "CID-TECH3"],
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_minimal(self):
        xml = (BASE_DATA_PATH / "responses/result_info_keyset_minimal.xml").read_bytes()
        result = InfoKeysetResult.parse(xml, SCHEMA)
        expected = [
            InfoKeysetResultData(
                roid="K0009907596-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-MYREG",
                cr_id=None,
                cr_date=None,
                up_id=None,
                up_date=None,
                tr_date=None,
                auth_info=None,
                id="KID-MYKEYSET",
                dnskeys=[],
                techs=["CID-TECH2"],
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = InfoKeysetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)


class TestInfoNssetResult(TestCase):
    def test_parse_full(self):
        xml = (BASE_DATA_PATH / "responses/result_info_nsset.xml").read_bytes()
        result = InfoNssetResult.parse(xml, SCHEMA)
        expected = [
            InfoNssetResultData(
                roid="N0009907595-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-MYREG",
                cr_id="REG-MYREG",
                cr_date=datetime(
                    2017, 7, 11, 13, 28, 42, tzinfo=timezone(timedelta(hours=2))
                ),
                up_id="REG-MYREG",
                up_date=datetime(
                    2017, 7, 27, 16, 54, 53, tzinfo=timezone(timedelta(hours=2))
                ),
                tr_date=None,
                auth_info=None,
                id="NID-MYNSSET",
                nss=[
                    Ns("ns1.mydomain.cz", ["111.222.111.222"]),
                    Ns("ns.otherdomain.cz", []),
                ],
                techs=["CID-TECH2", "CID-TECH3"],
                reportlevel=4,
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_full_minimal(self):
        xml = (BASE_DATA_PATH / "responses/result_info_nsset_minimal.xml").read_bytes()
        result = InfoNssetResult.parse(xml, SCHEMA)
        expected = [
            InfoNssetResultData(
                roid="N0009907595-CZ",
                statuses=[
                    Status(
                        "linked", "Has relation to other records in the registry", "en"
                    )
                ],
                cl_id="REG-MYREG",
                cr_id=None,
                cr_date=None,
                up_id=None,
                up_date=None,
                tr_date=None,
                auth_info=None,
                id="NID-MYNSSET",
                nss=[],
                techs=["CID-TECH2"],
                reportlevel=4,
            )
        ]

        self.assertEqual(result.code, 1000)
        self.assertEqual(result.res_data, expected)

    def test_parse_error(self):
        xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
        result = InfoNssetResult.parse(xml, SCHEMA)
        self.assertEqual(result.code, 2002)
