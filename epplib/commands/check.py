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
from typing import List, Sequence

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import CheckContactResult, CheckDomainResult, CheckKeysetResult, CheckNssetResult


class Check(Command):
    """Base class for EPP Check commands."""

    def _get_check_payload(self, namespace: str, schema_location: str, tag: str, items: Sequence[str]) -> Element:
        """Create subelements of the command tag specific for the Check command.

        Returns:
            Element with a list of items to check.
        """
        root = Element(QName(NAMESPACE.EPP, 'check'))

        item_check = SubElement(root, QName(namespace, 'check'))
        item_check.set(QName(NAMESPACE.XSI, 'schemaLocation'), schema_location)
        for item in items:
            SubElement(item_check, QName(namespace, tag)).text = item

        return root


@dataclass
class CheckDomain(Check):
    """EPP Domain Check command.

    Attributes:
        names: List of domains to check.
    """

    response_class = CheckDomainResult
    names: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckDomain.

        Returns:
            Element with a list of domains to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, 'name', self.names)


@dataclass
class CheckContact(Check):
    """EPP Check contact command.

    Attributes:
        ids: List of contacts to check.
    """

    response_class = CheckContactResult

    ids: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckContact.

        Returns:
            Element with a list of contacts to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.ids)


@dataclass
class CheckNsset(Check):
    """EPP Check nsset command.

    Attributes:
        ids: List of nssets to check.
    """

    response_class = CheckNssetResult

    ids: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckNsset.

        Returns:
            Element with a list of nssets to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, 'id', self.ids)


@dataclass
class CheckKeyset(Check):
    """EPP Check keyset command.

    Attributes:
        ids: List of keysets to check.
    """

    response_class = CheckKeysetResult

    ids: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckKeyset.

        Returns:
            Element with a list of keysets to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, 'id', self.ids)
