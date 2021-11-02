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

"""Module providing EPP commands."""
from dataclasses import dataclass

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import InfoContactResult, InfoDomainResult


class Info(Command):
    """Base class for EPP Info commands.

    Attributes:
        name: Domain name to query
    """

    def _get_info_payload(self, namespace: str, schema_location: str, tag: str, item: str) -> Element:
        """Create subelements specific for info command.

        Returns:
            Element with a domain to create.
        """
        info = Element(QName(NAMESPACE.EPP, 'info'))

        domain_info = SubElement(info, QName(namespace, 'info'))
        domain_info.set(QName(NAMESPACE.XSI, 'schemaLocation'), schema_location)

        SubElement(domain_info, QName(namespace, tag)).text = item

        return info


@dataclass
class InfoDomain(Info):
    """EPP Info Domain command.

    Attributes:
        name: Domain name to query
    """

    response_class = InfoDomainResult
    name: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CreateDomain.

        Returns:
            Element with a domain to create.
        """
        return self._get_info_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, 'name', self.name)


@dataclass
class InfoContact(Info):
    """EPP Info Contact command.

    Attributes:
        id: Contact id to query
    """

    response_class = InfoContactResult
    id: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CreateContact.

        Returns:
            Element with a contact to create.
        """
        return self._get_info_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.id)
