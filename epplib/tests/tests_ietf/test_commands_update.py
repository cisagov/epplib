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

from unittest.mock import patch

from typing import Any, Dict

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands import UpdateContact, UpdateDomain, UpdateHost
from epplib.models.common import (
    ContactAuthInfo,
    DomainAuthInfo,
    DomainContact,
    HostObjSet,
    HostStatus,
    Ip,
    Status,
)
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


@patch("epplib.commands.update.NAMESPACE", NAMESPACE)
@patch("epplib.commands.update.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.DomainAuthInfo.namespace", NAMESPACE.NIC_DOMAIN)
@patch("epplib.models.common.DomainContact.namespace", NAMESPACE.NIC_DOMAIN)
@patch("epplib.models.common.HostObjSet.namespace", NAMESPACE.NIC_DOMAIN)
@patch("epplib.models.common.Status.namespace", NAMESPACE.NIC_DOMAIN)
class TestUpdateDomain(XMLTestCase):
    params: Dict[str, Any] = {
        "name": "thisdomain.cz",
        "add": [
            Status("clientTransferProhibited", None),
            DomainContact("CID-MYCONTA", "tech"),
            HostObjSet(["ns1.thisdomain.cz", "ns2.thisdomain.cz"]),
        ],
        "rem": [
            Status("clientUpdateProhibited", None),
            DomainContact("CID-MYCONTT", "admin"),
            HostObjSet(["ns3.thisdomain.cz", "ns4.thisdomain.cz"]),
        ],
        "auth_info": DomainAuthInfo(pw="2fooBAR123fooBaz"),
    }

    def test_data(self):
        root = fromstring(UpdateDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.update(
                    domain.update(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name(self.params["name"]),
                        domain.add(
                            domain.status({"s": "clientTransferProhibited"}),
                            domain.contact({"type": "tech"}, "CID-MYCONTA"),
                            domain.ns(
                                domain.hostObj("ns1.thisdomain.cz"),
                                domain.hostObj("ns2.thisdomain.cz"),
                            ),
                        ),
                        domain.rem(
                            domain.status({"s": "clientUpdateProhibited"}),
                            domain.contact({"type": "admin"}, "CID-MYCONTT"),
                            domain.ns(
                                domain.hostObj("ns3.thisdomain.cz"),
                                domain.hostObj("ns4.thisdomain.cz"),
                            ),
                        ),
                        domain.chg(
                            domain.authInfo(
                                domain.pw(self.params["auth_info"].pw),
                            ),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


@patch("epplib.commands.update.NAMESPACE", NAMESPACE)
@patch("epplib.commands.update.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.ContactAuthInfo.namespace", NAMESPACE.NIC_CONTACT)
class TestUpdateContact(XMLTestCase):
    params: Dict[str, Any] = {
        "id": "CID-MYCONTA",
        "auth_info": ContactAuthInfo(pw="2fooBAR123fooBaz"),
    }

    def test_valid(self):
        self.assertRequestValid(UpdateContact, self.params, schema=SCHEMA)

    def test_data(self):
        root = fromstring(UpdateContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.update(
                    contact.update(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_CONTACT
                        },
                        contact.id(self.params["id"]),
                        contact.chg(
                            contact.authInfo(
                                contact.pw(self.params["auth_info"].pw),
                            ),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestUpdateHost(XMLTestCase):
    params: Dict[str, Any] = {
        "name": "ns1.thisdomain.cz",
        "add": [
            Ip(addr="192.0.2.2"),
            Ip(addr="1080:0:0:0:8:800:200C:417A", ip="v6"),
            HostStatus("clientDeleteProhibited"),
        ],
        "rem": [
            Ip(addr="192.0.3.3"),
            Ip(addr="2080:0:0:0:8:800:200D:417E", ip="v6"),
            HostStatus("clientUpdateProhibited"),
        ],
        "chg": "ns2.thisdomain.cz",
    }

    def test_valid(self):
        self.assertRequestValid(UpdateHost, self.params, schema=SCHEMA)

    def test_data(self):
        root = fromstring(UpdateHost(**self.params).xml())
        host = ElementMaker(namespace=NAMESPACE.NIC_HOST)
        expected = make_epp_root(
            EM.command(
                EM.update(
                    host.update(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_HOST
                        },
                        host.name(self.params["name"]),
                        host.add(
                            host.addr("192.0.2.2"),
                            host.addr(
                                {"ip": "v6"},
                                "1080:0:0:0:8:800:200C:417A",
                            ),
                            host.status({"s": "clientDeleteProhibited"}),
                        ),
                        host.rem(
                            host.addr("192.0.3.3"),
                            host.addr(
                                {"ip": "v6"},
                                "2080:0:0:0:8:800:200D:417E",
                            ),
                            host.status({"s": "clientUpdateProhibited"}),
                        ),
                        host.chg(
                            host.name(self.params["chg"]),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)
