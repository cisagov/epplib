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

"""Module providing EPP renew command."""
from dataclasses import dataclass
from datetime import date
from typing import Optional

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import Period
from epplib.responses import RenewDomainResult


@dataclass
class RenewDomain(Command):
    """EPP renew domain command.

    Attributes:
        name: Content of the command/renew/renew/name element.
        cur_exp_date: Content of the command/renew/renew/curExpDate element.
        period: Content of the command/renew/renew/period element.
    """

    response_class = RenewDomainResult

    name: str
    cur_exp_date: date
    period: Optional[Period] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for RenewDomain.

        Returns:
            Element with a list of domains to renew.
        """
        root = Element(QName(NAMESPACE.EPP, 'renew'))

        item_renew = SubElement(root, QName(NAMESPACE.NIC_DOMAIN, 'renew'))
        item_renew.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)
        SubElement(item_renew, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name
        SubElement(item_renew, QName(NAMESPACE.NIC_DOMAIN, 'curExpDate')).text = str(self.cur_exp_date)
        if self.period:
            item_renew.append(self.period.get_payload())

        return root
