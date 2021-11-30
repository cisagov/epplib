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

"""Module providing EPP delete commands."""
from dataclasses import dataclass

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import Result


class Delete(Command):
    """Base class for EPP Delete commands."""

    response_class = Result

    def _get_delete_payload(self, namespace: str, schema_location: str, tag: str, item: str) -> Element:
        """Create subelements of the command element specific for the Delete command.

        Returns:
            Element with the item to delete.
        """
        root = Element(QName(NAMESPACE.EPP, 'delete'))

        item_delete = SubElement(root, QName(namespace, 'delete'))
        item_delete.set(QName(NAMESPACE.XSI, 'schemaLocation'), schema_location)
        SubElement(item_delete, QName(namespace, tag)).text = item

        return root


@dataclass
class DeleteDomain(Delete):
    """EPP Domain Delete command.

    Attributes:
        name: Content of the epp/command/delete/delete/name element.
    """

    name: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for DeleteDomain.

        Returns:
            Element with a list of domains to delete.
        """
        return self._get_delete_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, 'name', self.name)


@dataclass
class DeleteContact(Delete):
    """EPP Delete contact command.

    Attributes:
        id: Content of the epp/command/delete/delete/id element.
    """

    id: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for DeleteContact.

        Returns:
            Element with the contact to delete.
        """
        return self._get_delete_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.id)


@dataclass
class DeleteKeyset(Delete):
    """EPP Delete keyset command.

    Attributes:
        id: Content of the epp/command/delete/delete/id element.
    """

    id: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for DeleteKeyset.

        Returns:
            Element with the keyset to delete.
        """
        return self._get_delete_payload(NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, 'id', self.id)


@dataclass
class DeleteNsset(Delete):
    """EPP Delete nsset command.

    Attributes:
        id: Content of the epp/command/delete/delete/id element.
    """

    id: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for DeleteNsset.

        Returns:
            Element with the nsset to delete.
        """
        return self._get_delete_payload(NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, 'id', self.id)
