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

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands import DeleteHost
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import EM, XMLTestCase, make_epp_root


class TestDeleteHost(XMLTestCase):
    host = "domain.cz"

    def test_valid(self):
        self.assertRequestValid(DeleteHost, {"name": self.host}, schema=SCHEMA)

    def test_data(self):
        root = fromstring(DeleteHost(self.host).xml())
        host = ElementMaker(namespace=NAMESPACE.NIC_HOST)
        expected = make_epp_root(
            EM.command(
                EM.delete(
                    host.delete(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_HOST
                        },
                        host.name(self.host),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
