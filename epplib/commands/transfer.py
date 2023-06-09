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

"""Module providing EPP transfer commands."""
from dataclasses import dataclass
from typing import Union

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import AuthInfo
from epplib.responses import Result


class Transfer(Command):
    """Base class for EPP Transfer commands."""

    response_class = Result
    auth_info: str

    def _get_transfer_payload(
        self, namespace: str, schema_location: str, tag: str, item: str
    ) -> Element:
        """Create subelements of the command element specific for the Transfer command.

        Returns:
            Element with a the item to transfer.
        """
        root = Element(QName(NAMESPACE.EPP, "transfer"), op="request")

        item_transfer = SubElement(root, QName(namespace, "transfer"))
        item_transfer.set(QName(NAMESPACE.XSI, "schemaLocation"), schema_location)
        SubElement(item_transfer, QName(namespace, tag)).text = item
        if isinstance(self.auth_info, str):
            SubElement(
                item_transfer, QName(namespace, "authInfo")
            ).text = self.auth_info
        elif isinstance(self.auth_info, AuthInfo):
            item_transfer.append(self.auth_info.get_payload())

        return root


@dataclass
class TransferDomain(Transfer):
    """EPP Domain Transfer command.

    Attributes:
        name: Content of command/transfer/transfer/name element.
        auth_info: Content of command/transfer/transfer/auth_info element.
    """

    name: str
    auth_info: Union[str, AuthInfo]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for TransferDomain.

        Returns:
            Element with a domain to transfer.
        """
        return self._get_transfer_payload(
            NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, "name", self.name
        )


@dataclass
class TransferContact(Transfer):
    """EPP Contact Transfer command.

    Attributes:
        id: Content of command/transfer/transfer/id element.
        auth_info: Content of command/transfer/transfer/auth_info element.
    """

    id: str
    auth_info: Union[str, AuthInfo]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for TransferContact.

        Returns:
            Element with a contact to transfer.
        """
        return self._get_transfer_payload(
            NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, "id", self.id
        )


@dataclass
class TransferKeyset(Transfer):
    """EPP Keyset Transfer command.

    Attributes:
        id: Content of command/transfer/transfer/id element.
        auth_info: Content of command/transfer/transfer/auth_info element.
    """

    id: str
    auth_info: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for TransferKeyset.

        Returns:
            Element with a keyset to transfer.
        """
        return self._get_transfer_payload(
            NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, "id", self.id
        )


@dataclass
class TransferNsset(Transfer):
    """EPP Nsset Transfer command.

    Attributes:
        id: Content of command/transfer/transfer/id element.
        auth_info: Content of command/transfer/transfer/auth_info element.
    """

    id: str
    auth_info: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for TransferNsset.

        Returns:
            Element with a nsset to transfer.
        """
        return self._get_transfer_payload(
            NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, "id", self.id
        )
