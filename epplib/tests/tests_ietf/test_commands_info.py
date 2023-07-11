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

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands.info import InfoContact, InfoDomain, InfoHost
from epplib.models.common import ContactAuthInfo, DomainAuthInfo
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


@patch("epplib.commands.info.NAMESPACE", NAMESPACE)
@patch("epplib.commands.info.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.DomainAuthInfo.namespace", NAMESPACE.NIC_DOMAIN)
class TestInfoDomain(XMLTestCase):
    def setUp(self) -> None:
        """Setup params."""
        self.params = {
            "name": "mydoma.in",
            "auth_info": DomainAuthInfo(pw="2fooBAR123fooBaz"),
        }

    def test_valid(self):
        self.assertRequestValid(InfoDomain, self.params, schema=SCHEMA)

    def test_data_auth_info_object(self):
        root = fromstring(InfoDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    domain.info(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name(self.params["name"]),
                        domain.authInfo(
                            domain.pw(self.params["auth_info"].pw),
                        ),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


@patch("epplib.commands.info.NAMESPACE", NAMESPACE)
@patch("epplib.commands.info.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.ContactAuthInfo.namespace", NAMESPACE.NIC_CONTACT)
class TestInfoContact(XMLTestCase):
    def setUp(self) -> None:
        """Setup params."""
        self.params = {
            "id": "CID-MYCONTACT",
            "auth_info": ContactAuthInfo(pw="2fooBAR123fooBaz"),
        }

    def test_valid(self):
        self.assertRequestValid(InfoContact, self.params, schema=SCHEMA)

    def test_data_auth_info_object(self):
        root = fromstring(InfoContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    contact.info(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_CONTACT
                        },
                        contact.id(self.params["id"]),
                        contact.authInfo(contact.pw(self.params["auth_info"].pw)),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestInfoHost(XMLTestCase):
    def setUp(self) -> None:
        """Setup params."""
        self.params = {"name": "ns1.mydoma.in"}

    def test_valid(self):
        self.assertRequestValid(InfoHost, self.params, schema=SCHEMA)

    def test_data(self):
        root = fromstring(InfoHost(**self.params).xml())
        host = ElementMaker(namespace=NAMESPACE.NIC_HOST)
        expected = make_epp_root(
            EM.command(
                EM.info(
                    host.info(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_HOST
                        },
                        host.name(self.params["name"]),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
