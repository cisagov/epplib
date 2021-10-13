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

from epplib.commands import CreateDomain
from epplib.constants import NAMESPACE, SCHEMA_LOCATION, Unit
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
