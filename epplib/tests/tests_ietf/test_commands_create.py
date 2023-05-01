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

from unittest.mock import patch

from typing import Any, Dict

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands import CreateContact, CreateDomain, CreateHost
from epplib.models.common import ContactAuthInfo, DomainAuthInfo
from epplib.models import ContactAddr, Ip
from epplib.models.create import CreatePostalInfo
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


@patch('epplib.commands.create.NAMESPACE', NAMESPACE)
@patch('epplib.commands.create.SCHEMA_LOCATION', SCHEMA_LOCATION)
@patch('epplib.models.common.DomainAuthInfo.namespace', NAMESPACE.NIC_DOMAIN)
class TestCreateDomain(XMLTestCase):
    params: Dict[str, Any] = {
        'name': 'thisdomain.cz',
        'registrant': 'CID-MYOWN',
        'auth_info': DomainAuthInfo(pw='2fooBAR123fooBaz'),
    }

    def test_valid(self):
        self.assertRequestValid(CreateDomain, self.params, schema=SCHEMA)

    def test_data_auth_info_object(self):
        root = fromstring(CreateDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    domain.create(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                        domain.registrant(self.params['registrant']),
                        domain.authInfo(
                            domain.pw(self.params['auth_info'].pw),
                        ),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


@patch('epplib.commands.create.NAMESPACE', NAMESPACE)
@patch('epplib.commands.create.SCHEMA_LOCATION', SCHEMA_LOCATION)
@patch('epplib.models.common.ContactAuthInfo.namespace', NAMESPACE.NIC_CONTACT)
@patch('epplib.models.create.CreatePostalInfo.namespace', NAMESPACE.NIC_CONTACT)
@patch('epplib.models.ContactAddr.namespace', NAMESPACE.NIC_CONTACT)
class TestCreateContact(XMLTestCase):
    params: Dict[str, Any] = {
        'id': 'CID-MYCONTACT',
        'postal_info': CreatePostalInfo(
            'John Doe',
            ContactAddr(
               ['Street 123'],
               'City',
               '12300',
               'CZ'
            ),
            type='loc'
        ),
        'email': 'john@doe.cz',
        'auth_info': ContactAuthInfo(pw='2fooBAR123fooBaz'),
    }

    def test_valid(self):
        self.assertRequestValid(CreateContact, self.params, schema=SCHEMA)

    def test_data(self):
        root = fromstring(CreateContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    contact.create(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params['id']),
                        contact.postalInfo(
                            {'type': self.params['postal_info'].type},
                            contact.name(self.params['postal_info'].name),
                            contact.addr(
                                contact.street(self.params['postal_info'].addr.street[0]),
                                contact.city(self.params['postal_info'].addr.city),
                                contact.pc(self.params['postal_info'].addr.pc),
                                contact.cc(self.params['postal_info'].addr.cc),
                            ),
                        ),
                        contact.email(self.params['email']),
                        contact.authInfo(
                            contact.pw(self.params['auth_info'].pw),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreateHost(XMLTestCase):
    params: Dict[str, Any] = {
        'name': 'ns1.thisdomain.cz',
        'addrs': [
            Ip('192.0.2.2'),
            Ip('1080:0:0:0:8:800:200C:417A', 'v6'),
        ],
    }

    def test_valid(self):
        self.assertRequestValid(CreateHost, self.params, schema=SCHEMA)

    def test_data(self):
        root = fromstring(CreateHost(**self.params).xml())
        host = ElementMaker(namespace=NAMESPACE.NIC_HOST)
        expected = make_epp_root(
            EM.command(
                EM.create(
                    host.create(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_HOST},
                        host.name(self.params['name']),
                        *[addr.get_payload() for addr in self.params['addrs']],
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)
