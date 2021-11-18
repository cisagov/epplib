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

from epplib.commands import UpdateDomain
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
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
