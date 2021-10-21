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

from datetime import date
from typing import Any, Dict, Mapping

from lxml.builder import ElementMaker
from lxml.etree import QName

from epplib.commands import CreateContact, CreateDomain
from epplib.commands.command_extensions import CreateContactMailingAddressExtension, CreateDomainEnumExtension
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import ContactAddr, ExtraAddr, PostalInfo
from epplib.tests.utils import XMLTestCase, sub_dict


class TestCreateDomainEnumExtension(XMLTestCase):
    command_params: Dict[str, Any] = {
        'name': 'thisdomain.cz',
        'registrant': 'CID-MYOWN',
    }
    extension_params: Dict[str, Any] = {
        'val_ex_date': date(2021, 1, 1),
        'publish': True,
    }

    def test_valid(self):
        params = (
            tuple(self.extension_params.keys()),
            ['val_ex_date'],
            ['publish'],
        )
        for subset in params:
            with self.subTest(params=subset):
                extension = CreateDomainEnumExtension(**sub_dict(self.extension_params, subset))
                self.assertRequestValid(CreateDomain, self.command_params, extension=extension)

    def test_data(self):
        extension = CreateDomainEnumExtension(**self.extension_params)

        enumval = ElementMaker(namespace=NAMESPACE.NIC_ENUMVAL)
        expected = enumval.create(
            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_ENUMVAL},
            enumval.valExDate('2021-01-01'),
            enumval.publish('true'),
        )

        self.assertXMLEqual(extension.get_payload(), expected)


class TestCreateContactMailingAddressExtension(XMLTestCase):

    addr_params: Mapping[str, Any] = {
        'street': ['Door 42', 'Street 123'],
        'city': 'City',
        'pc': '12300',
        'cc': 'CZ',
        'sp': 'Province',
    }

    def test_valid(self):
        command_params: Dict[str, Any] = {
            'id': 'CID-MYCONTACT',
            'postal_info': PostalInfo(
                'John Doe',
                ContactAddr(**self.addr_params),
            ),
            'email': 'john@doe.cz',
        }
        extension = CreateContactMailingAddressExtension(ExtraAddr(**self.addr_params))
        self.assertRequestValid(CreateContact, command_params, extension)

    def test_data(self):
        extension = CreateContactMailingAddressExtension(ExtraAddr(**self.addr_params))
        EM = ElementMaker(namespace=NAMESPACE.NIC_EXTRA_ADDR)
        expected = EM.create(
            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_EXTRA_ADDR},
            EM.mailing(
                EM.addr(
                    EM.street(self.addr_params['street'][0]),
                    EM.street(self.addr_params['street'][1]),
                    EM.city(self.addr_params['city']),
                    EM.sp(self.addr_params['sp']),
                    EM.pc(self.addr_params['pc']),
                    EM.cc(self.addr_params['cc']),
                )
            )
        )
        self.assertXMLEqual(extension.get_payload(), expected)
