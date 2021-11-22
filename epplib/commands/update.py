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

"""Module providing EPP update commands."""
from dataclasses import dataclass, field
from typing import Optional, Sequence

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import Result


@dataclass
class UpdateDomain(Command):
    """EPP update domain command.

    Attributes:
        name: Content of epp/command/update/update/name
        add: Content of epp/command/update/update/add/admin
        rem: Content of epp/command/update/update/rem/admin
        nsset: Content of epp/command/update/update/chg/nsset
        keyset: Content of epp/command/update/update/chg/keyset
        registrant: Content of epp/command/update/update/chg/registrant
        auth_info: Content of epp/command/update/update/chg/authInfo
    """

    response_class = Result

    name: str
    add: Sequence[str] = field(default_factory=list)
    rem: Sequence[str] = field(default_factory=list)
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    registrant: Optional[str] = None
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for UpdateDomain.

        Returns:
            Element with a domain to update.
        """
        update = Element(QName(NAMESPACE.EPP, 'update'))

        domain_update = SubElement(update, QName(NAMESPACE.NIC_DOMAIN, 'update'))
        domain_update.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)

        SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name

        if self.add:
            add = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'add'))
            for item in self.add:
                SubElement(add, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = item

        if self.rem:
            rem = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'rem'))
            for item in self.rem:
                SubElement(rem, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = item

        if self.nsset or self.keyset or self.registrant or self.auth_info:
            chg = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'chg'))
            if self.nsset is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'nsset')).text = self.nsset
            if self.keyset is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'keyset')).text = self.keyset
            if self.registrant is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'registrant')).text = self.registrant
            if self.auth_info is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'authInfo')).text = self.auth_info

        return update
