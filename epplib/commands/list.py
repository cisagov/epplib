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

"""Module providing EPP list commands."""
from typing import ClassVar

from lxml.etree import Element, QName

from epplib.commands.extensions import FredExtCommand
from epplib.constants import NAMESPACE
from epplib.responses import ListResult


class List(FredExtCommand):
    """Base class for List commands."""

    response_class = ListResult
    tag: ClassVar[str]

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for List command.

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
