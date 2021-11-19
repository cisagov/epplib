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
from lxml.etree import QName, fromstring

from epplib.commands import UpdateContact, UpdateDomain
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import ContactAddr, Disclose, DiscloseField, Ident, IdentType, PostalInfo
from epplib.tests.utils import EM, XMLTestCase, make_epp_root, sub_dict


class TestUpdateDomain(XMLTestCase):
    params: Dict[str, Any] = {
        'name': 'thisdomain.cz',
        'add': ['CID-ADMIN1', 'CID-ADMIN2'],
        'rem': ['CID-ADMIN3', 'CID-ADMIN4'],
        'nsset': 'NID-MYNSSET',
        'keyset': 'KID-MYKEYSET',
        'registrant': 'CID-MYOWN',
        'auth_info': '12345',
    }
    required = ['name']

    def test_valid(self):
        self.assertRequestValid(UpdateDomain, self.params)
        self.assertRequestValid(UpdateDomain, sub_dict(self.params, self.required))

    def test_data_full(self):
        root = fromstring(UpdateDomain(**self.params).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.update(
                    domain.update(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                        domain.name(self.params['name']),
                        domain.add(
                            domain.admin('CID-ADMIN1'),
                            domain.admin('CID-ADMIN2'),
                        ),
                        domain.rem(
                            domain.admin('CID-ADMIN3'),
                            domain.admin('CID-ADMIN4'),
                        ),
                        domain.chg(
                            domain.nsset(self.params['nsset']),
                            domain.keyset(self.params['keyset']),
                            domain.registrant(self.params['registrant']),
                            domain.authInfo(self.params['auth_info']),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_required(self):
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)

        tags = (
            ('nsset', 'nsset'),
            ('keyset', 'keyset'),
            ('registrant', 'registrant'),
            ('authInfo', 'auth_info'),
        )
        for tag, variable in tags:
            with self.subTest(tag=tag):
                root = fromstring(UpdateDomain(**sub_dict(self.params, self.required + [variable])).xml())
                expected = make_epp_root(
                    EM.command(
                        EM.update(
                            domain.update(
                                {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                                domain.name(self.params['name']),
                                domain.chg(
                                    domain(tag, self.params[variable]),
                                ),
                            ),
                        ),
                    )
                )
                self.assertXMLEqual(root, expected)


class TestUpdateContact(XMLTestCase):
    params: Dict[str, Any] = {
        'id': 'CID-MYCONTA',
        'postal_info': PostalInfo('John Doe', ContactAddr(street=['The Street'], city='City', pc='abc', cc='CZ')),
        'voice': '+420.222123456',
        'fax': '+420.222123457',
        'email': 'john@doe.cz',
        'auth_info': 'trnpwd',
        'disclose': Disclose(True, set((DiscloseField.VOICE,))),
        'vat': '1312112029',
        'ident': Ident(IdentType.PASSPORT, '12345'),
        'notify_email': 'notify.john@doe.cz',
    }
    required = ['id']

    def test_valid(self):
        self.assertRequestValid(UpdateContact, self.params)
        self.assertRequestValid(UpdateContact, sub_dict(self.params, self.required))

    def test_data_full(self):
        root = fromstring(UpdateContact(**self.params).xml())
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        expected = make_epp_root(
            EM.command(
                EM.update(
                    contact.update(
                        {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                        contact.id(self.params['id']),
                        contact.chg(
                            self.params['postal_info'].get_payload(),
                            contact.voice(self.params['voice']),
                            contact.fax(self.params['fax']),
                            contact.email(self.params['email']),
                            contact.authInfo(self.params['auth_info']),
                            self.params['disclose'].get_payload(),
                            contact.vat(self.params['vat']),
                            self.params['ident'].get_payload(),
                            contact.notifyEmail(self.params['notify_email']),
                        ),
                    ),
                ),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_required(self):
        contact = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)

        tags = (
            ('postalInfo', 'postal_info'),
            ('voice', 'voice'),
            ('fax', 'fax'),
            ('email', 'email'),
            ('authInfo', 'auth_info'),
            ('disclose', 'disclose'),
            ('vat', 'vat'),
            ('ident', 'ident'),
            ('notifyEmail', 'notify_email'),
        )
        for tag, variable in tags:
            with self.subTest(tag=tag):
                param = self.params[variable]
                params = {**sub_dict(self.params, self.required), variable: param}
                root = fromstring(UpdateContact(**params).xml())

                if hasattr(param, 'get_payload'):
                    element = param.get_payload()
                else:
                    element = contact(tag, param)

                expected = make_epp_root(
                    EM.command(
                        EM.update(
                            contact.update(
                                {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_CONTACT},
                                contact.id(self.params['id']),
                                contact.chg(
                                    element
                                ),
                            ),
                        ),
                    )
                )
                self.assertXMLEqual(root, expected)
