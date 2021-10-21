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

from typing import Any, Dict

from lxml.builder import ElementMaker
from lxml.etree import Element, QName, fromstring

from epplib.commands import CreateContact, CreateDomain
from epplib.constants import NAMESPACE, SCHEMA_LOCATION, Unit
from epplib.models import ContactAddr, Disclose, DiscloseFields, Ident, IdentType, PostalInfo
from epplib.tests.utils import EM, XMLTestCase, make_epp_root, sub_dict


class TestCreateDomain(XMLTestCase):
    params: Dict[str, Any] = {
        'name': 'thisdomain.cz',
        'period': 2,
        'unit': Unit.MONTH,
        'nsset': 'NID-MYNSSET',
        'keyset': 'KID-MYKEYSET',
        'registrant': 'CID-MYOWN',
        'admin': 'CID-ADMIN1',
        'auth_info': '12345',
    }
    required = ['name', 'registrant']

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
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                        domain.period(str(self.params['period']), unit=self.params['unit'].value),
                        domain.nsset(self.params['nsset']),
                        domain.keyset(self.params['keyset']),
                        domain.registrant(self.params['registrant']),
                        domain.admin(self.params['admin']),
                        domain.authInfo(self.params['auth_info']),
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
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                        domain.registrant(self.params['registrant']),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreateContact(XMLTestCase):
    params_required: Dict[str, Any] = {
        'id': 'CID-MYCONTACT',
        'postal_info': PostalInfo(
            'John Doe',
            ContactAddr(
               ['Street 123'],
               'City',
               '12300',
               'CZ'
            ),
        ),
        'email': 'john@doe.cz',
    }

    params_full: Dict[str, Any] = {
        'id': 'CID-MYCONTACT',
        'postal_info': PostalInfo(
            'John Doe',
            ContactAddr(
               ['Door 42', 'Street 123'],
               'City',
               '12300',
               'CZ',
               'Province',
            ),
            'Company X Ltd.',
        ),
        'voice': '+420.222123456',
        'fax': '+420.222123457',
        'email': 'john@doe.cz',
        'auth_info': 'trnpwd',
        'disclose': Disclose(True, set([DiscloseFields.VAT, DiscloseFields.EMAIL])),
        'vat': '1312112029',
        'ident': Ident(IdentType.OP, '12345'),
        'notify_email': 'notify-john@doe.cz',
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
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params_required['id']),
                        contact.postalInfo(
                            contact.name(self.params_required['postal_info'].name),
                            contact.addr(
                                contact.street(self.params_required['postal_info'].addr.street[0]),
                                contact.city(self.params_required['postal_info'].addr.city),
                                contact.pc(self.params_required['postal_info'].addr.pc),
                                contact.cc(self.params_required['postal_info'].addr.cc),
                            ),
                        ),
                        contact.email(self.params_required['email']),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_full(self):
        root = fromstring(CreateContact(**self.params_full).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        disclose_fields = [
            Element(QName(NAMESPACE.NIC_CONTACT, f)) for f in sorted(self.params_full['disclose'].fields)
        ]
        expected = make_epp_root(
            EM.command(
                EM.create(
                    contact.create(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params_full['id']),
                        contact.postalInfo(
                            contact.name(self.params_full['postal_info'].name),
                            contact.org(self.params_full['postal_info'].org),
                            contact.addr(
                                contact.street(self.params_full['postal_info'].addr.street[0]),
                                contact.street(self.params_full['postal_info'].addr.street[1]),
                                contact.city(self.params_full['postal_info'].addr.city),
                                contact.sp(self.params_full['postal_info'].addr.sp),
                                contact.pc(self.params_full['postal_info'].addr.pc),
                                contact.cc(self.params_full['postal_info'].addr.cc),
                            ),
                        ),
                        contact.voice(self.params_full['voice']),
                        contact.fax(self.params_full['fax']),
                        contact.email(self.params_full['email']),
                        contact.authInfo(self.params_full['auth_info']),
                        contact.disclose(
                            *disclose_fields,
                            flag='1' if self.params_full['disclose'].flag else '0'
                        ),
                        contact.vat(self.params_full['vat']),
                        contact.ident(self.params_full['ident'].value, type=self.params_full['ident'].type.value),
                        contact.notifyEmail(self.params_full['notify_email']),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)
