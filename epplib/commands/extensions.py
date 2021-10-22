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

"""Module providing base EPP commands."""
from abc import abstractmethod

from lxml.etree import Element, QName

from epplib.commands import Request
from epplib.constants import NAMESPACE


class Extension(Request):
    """Base class for EPP Extensions."""

    def _get_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the epp tag specific for the given Command.

        Returns:
            Element with the Extension payload.
        """
        extension_element = Element(QName(NAMESPACE.EPP, 'extension'))
        extension_element.append(self._get_extension_payload())

        return extension_element

    @abstractmethod
    def _get_extension_payload(self) -> Element:
        """Create subelements of the extension tag specific for the given Extension subclass.

        Returns:
            Element with the Extension specific payload.
        """
