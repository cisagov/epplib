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
from typing import Any, Mapping

from lxml.builder import ElementMaker
from lxml.etree import QName, fromstring

from epplib.commands import RenewDomain
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import Period, Unit
from epplib.tests.utils import EM, XMLTestCase, make_epp_root, sub_dict


class TestRenewDomain(XMLTestCase):
    params_full: Mapping[str, Any] = {
        "name": "mydomain.cz",
        "cur_exp_date": date(2018, 7, 11),
        "period": Period(2, Unit.YEAR),
    }
    params_required = sub_dict(params_full, ["name", "cur_exp_date"])

    def test_valid(self):
        self.assertRequestValid(RenewDomain, self.params_required)
        self.assertRequestValid(RenewDomain, self.params_full)

    def test_data_full(self):
        root = fromstring(RenewDomain(**self.params_full).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.renew(
                    domain.renew(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name("mydomain.cz"),
                        domain.curExpDate("2018-07-11"),
                        domain.period("2", unit="y"),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)

    def test_data_required(self):
        root = fromstring(RenewDomain(**self.params_required).xml())
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.command(
                EM.renew(
                    domain.renew(
                        {
                            QName(
                                NAMESPACE.XSI, "schemaLocation"
                            ): SCHEMA_LOCATION.NIC_DOMAIN
                        },
                        domain.name("mydomain.cz"),
                        domain.curExpDate("2018-07-11"),
                    )
                )
            )
        )
        self.assertXMLEqual(root, expected)
