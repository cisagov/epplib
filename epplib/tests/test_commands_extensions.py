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
from typing import Any, Dict

from lxml.builder import ElementMaker
from lxml.etree import QName

from epplib.commands import CreateDomain
from epplib.commands.extensions import CreateDomainEnumExtension
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
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
