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

from typing import Any, Dict

from lxml.builder import ElementMaker
from lxml.etree import Element, QName, fromstring

from epplib.commands import CreateContact, CreateDomain, CreateKeyset, CreateNsset
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import (
    ContactAddr,
    Disclose,
    DiscloseField,
    Dnskey,
    Ident,
    IdentType,
    Ns,
    Period,
    Unit,
)
from epplib.models.create import CreatePostalInfo
from epplib.tests.utils import EM, XMLTestCase, make_epp_root, sub_dict


class TestCreateDomain(XMLTestCase):
    params: Dict[str, Any] = {
        "name": "thisdomain.cz",
        "period": Period(2, Unit.MONTH),
        "nsset": "NID-MYNSSET",
        "keyset": "KID-MYKEYSET",
        "registrant": "CID-MYOWN",
        "admins": ["CID-ADMIN1", "CID-ADMIN2"],
        "auth_info": "12345",
    }
    required = ["name", "registrant"]

    def test_valid(self):
        self.assertRequestValid(CreateDomain, self.params)
        self.assertRequestValid(CreateDomain, sub_dict(self.params, self.required))

    def test_data_full(self):
        root = fromstring(CreateDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    domain.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name(self.params["name"]),
                        domain.period(
                            str(self.params["period"].length),
                            unit=self.params["period"].unit.value,
                        ),
                        domain.nsset(self.params["nsset"]),
                        domain.keyset(self.params["keyset"]),
                        domain.registrant(self.params["registrant"]),
                        domain.admin(self.params["admins"][0]),
                        domain.admin(self.params["admins"][1]),
                        domain.authInfo(self.params["auth_info"]),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_required(self):
        root = fromstring(CreateDomain(**sub_dict(self.params, self.required)).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    domain.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name(self.params["name"]),
                        domain.registrant(self.params["registrant"]),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreateContact(XMLTestCase):
    params_required: Dict[str, Any] = {
        "id": "CID-MYCONTACT",
        "postal_info": CreatePostalInfo(
            "John Doe",
            ContactAddr(["Street 123"], "City", "12300", "CZ"),
        ),
        "email": "john@doe.cz",
    }

    params_full: Dict[str, Any] = {
        "id": "CID-MYCONTACT",
        "postal_info": CreatePostalInfo(
            "John Doe",
            ContactAddr(
                ["Door 42", "Street 123"],
                "City",
                "12300",
                "CZ",
                "Province",
            ),
            "Company X Ltd.",
        ),
        "voice": "+420.222123456",
        "fax": "+420.222123457",
        "email": "john@doe.cz",
        "auth_info": "trnpwd",
        "disclose": Disclose(True, set([DiscloseField.NAME, DiscloseField.EMAIL, DiscloseField.VAT])),
        "vat": "1312112029",
        "ident": Ident(IdentType.OP, "12345"),
        "notify_email": "notify-john@doe.cz",
    }

    def test_valid(self):
        self.assertRequestValid(CreateContact, self.params_required)
        self.assertRequestValid(CreateContact, self.params_full)

    def test_data_required(self):
        root = fromstring(CreateContact(**self.params_required).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    contact.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_CONTACT
                        },
                        contact.id(self.params_required["id"]),
                        contact.postalInfo(
                            contact.name(self.params_required["postal_info"].name),
                            contact.addr(
                                contact.street(
                                    self.params_required["postal_info"].addr.street[0]
                                ),
                                contact.city(
                                    self.params_required["postal_info"].addr.city
                                ),
                                contact.pc(self.params_required["postal_info"].addr.pc),
                                contact.cc(self.params_required["postal_info"].addr.cc),
                            ),
                        ),
                        contact.email(self.params_required["email"]),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_full(self):
        root = fromstring(CreateContact(**self.params_full).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose_fields = [
            Element(QName(NAMESPACE.NIC_CONTACT, f))
            for f in [DiscloseField.NAME, DiscloseField.EMAIL, DiscloseField.VAT]
        ]
        expected = make_epp_root(
            EM.command(
                EM.create(
                    contact.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_CONTACT
                        },
                        contact.id(self.params_full["id"]),
                        contact.postalInfo(
                            contact.name(self.params_full["postal_info"].name),
                            contact.org(self.params_full["postal_info"].org),
                            contact.addr(
                                contact.street(
                                    self.params_full["postal_info"].addr.street[0]
                                ),
                                contact.street(
                                    self.params_full["postal_info"].addr.street[1]
                                ),
                                contact.city(self.params_full["postal_info"].addr.city),
                                contact.sp(self.params_full["postal_info"].addr.sp),
                                contact.pc(self.params_full["postal_info"].addr.pc),
                                contact.cc(self.params_full["postal_info"].addr.cc),
                            ),
                        ),
                        contact.voice(self.params_full["voice"]),
                        contact.fax(self.params_full["fax"]),
                        contact.email(self.params_full["email"]),
                        contact.authInfo(self.params_full["auth_info"]),
                        contact.disclose(
                            *disclose_fields,
                            flag="1" if self.params_full["disclose"].flag else "0",
                        ),
                        contact.vat(self.params_full["vat"]),
                        contact.ident(
                            self.params_full["ident"].value,
                            type=self.params_full["ident"].type.value,
                        ),
                        contact.notifyEmail(self.params_full["notify_email"]),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreateNsset(XMLTestCase):
    params: Dict[str, Any] = {
        "id": "NID-ANSSET",
        "nss": [
            Ns("ns1.domain.cz"),
            Ns("ns2.domain.cz", ["217.31.207.130", "217.31.207.131"]),
        ],
        "tech": ["CID-TECH1", "CID-TECH2"],
        "auth_info": "abc123",
        "reportlevel": 1,
    }
    required = ["id", "nss", "tech"]

    def test_valid(self):
        self.assertRequestValid(CreateNsset, self.params)
        self.assertRequestValid(CreateNsset, sub_dict(self.params, self.required))

    def test_data_full(self):
        root = fromstring(CreateNsset(**self.params).xml())
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    nsset.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_NSSET
                        },
                        nsset.id(self.params["id"]),
                        *[ns.get_payload() for ns in self.params["nss"]],
                        nsset.tech(self.params["tech"][0]),
                        nsset.tech(self.params["tech"][1]),
                        nsset.authInfo(self.params["auth_info"]),
                        nsset.reportlevel(str(self.params["reportlevel"])),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_required(self):
        root = fromstring(CreateNsset(**sub_dict(self.params, self.required)).xml())
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    nsset.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_NSSET
                        },
                        nsset.id(self.params["id"]),
                        *[ns.get_payload() for ns in self.params["nss"]],
                        nsset.tech(self.params["tech"][0]),
                        nsset.tech(self.params["tech"][1]),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreateKeyset(XMLTestCase):
    params: Dict[str, Any] = {
        "id": "NID-AKEYSET",
        "dnskeys": [
            Dnskey(
                257, 3, 5, "AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg8"
            ),
            Dnskey(
                257, 3, 5, "AwEAAddt2AkLfYGKgiEZB5SmIF8EvrjxNMH6HtxWEA4RJ9Ao6LCWheg9"
            ),
        ],
        "tech": ["CID-TECH1", "CID-TECH2"],
        "auth_info": "abc123",
    }
    required = ["id", "dnskeys", "tech"]

    def test_valid(self):
        self.assertRequestValid(CreateKeyset, self.params)
        self.assertRequestValid(CreateKeyset, sub_dict(self.params, self.required))

    def test_data_full(self):
        root = fromstring(CreateKeyset(**self.params).xml())
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    keyset.create(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_KEYSET
                        },
                        keyset.id(self.params["id"]),
                        *[dk.get_payload() for dk in self.params["dnskeys"]],
                        keyset.tech(self.params["tech"][0]),
                        keyset.tech(self.params["tech"][1]),
                        keyset.authInfo(self.params["auth_info"]),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)
