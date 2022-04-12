#
# Copyright (C) 2021-2022  CZ.NIC, z. s. p. o.
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

"""Module providing EPP list commands."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from lxml.etree import Element, QName, SubElement

from epplib.commands.extensions import FredExtCommand
from epplib.constants import NAMESPACE
from epplib.responses import GetResultsResult, ListResult


class List(FredExtCommand):
    """Base class for List commands."""

    response_class = ListResult
    tag: ClassVar[str]

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension element specific for List command.

        Returns:
            Element with List request payload.
        """
        root = super()._get_extension_payload(tr_id)
        root.insert(0, Element(QName(NAMESPACE.FRED, self.tag)))

        return root


class ListDomains(List):
    """List domain command."""

    tag = 'listDomains'


class ListContacts(List):
    """List domain command."""

    tag = 'listContacts'


class ListKeysets(List):
    """List domain command."""

    tag = 'listKeysets'


class ListNssets(List):
    """List domain command."""

    tag = 'listNssets'


class ListBy(FredExtCommand):
    """Base class for ListBy commands."""

    response_class = ListResult

    command_tag: ClassVar[str]
    item_tag: ClassVar[str]

    @abstractmethod
    def _get_item_id(self) -> str:
        """Get id or name of the item."""

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension element specific for ListBy command.

        Returns:
            Element with List request payload.
        """
        root = super()._get_extension_payload(tr_id)
        command = Element(QName(NAMESPACE.FRED, self.command_tag))
        SubElement(command, QName(NAMESPACE.FRED, self.item_tag)).text = self._get_item_id()
        root.insert(0, command)

        return root


@dataclass
class ListDomainsByContact(ListBy):
    """List domains by contact command."""

    command_tag = 'domainsByContact'
    item_tag = 'id'

    id: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.id


@dataclass
class ListDomainsByNsset(ListBy):
    """List domains by nsset command."""

    command_tag = 'domainsByNsset'
    item_tag = 'id'

    id: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.id


@dataclass
class ListDomainsByKeyset(ListBy):
    """List domains by keyset command."""

    command_tag = 'domainsByKeyset'
    item_tag = 'id'

    id: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.id


@dataclass
class ListNssetsByContact(ListBy):
    """List nssets by contact command."""

    command_tag = 'nssetsByContact'
    item_tag = 'id'

    id: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.id


@dataclass
class ListKeysetsByContact(ListBy):
    """List keysets by contact command."""

    command_tag = 'keysetsByContact'
    item_tag = 'id'

    id: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.id


@dataclass
class ListNssetsByNs(ListBy):
    """List nssets by ns command."""

    command_tag = 'nssetsByNs'
    item_tag = 'name'

    name: str

    def _get_item_id(self) -> str:
        """Get id or name of the item."""
        return self.name


class GetResults(FredExtCommand):
    """Get results command."""

    response_class = GetResultsResult

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension element specific for Get results command.

        Returns:
            Element with get results payload.
        """
        root = super()._get_extension_payload(tr_id)
        root.insert(0, Element(QName(NAMESPACE.FRED, 'getResults')))

        return root
