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

"""Module providing means to process responses to EPP commands."""
from abc import ABC, abstractmethod

from lxml.etree import Element, QName, fromstring  # nosec - TODO: Fix lxml security issues

from epplib.constants import NAMESPACE_EPP


class Response(ABC):
    """Base class for responses to EPP commands."""

    def __init__(self, raw_response: bytes):
        root = fromstring(raw_response)

        if root.tag != QName(NAMESPACE_EPP, 'epp'):
            raise ValueError('Root element has to be "epp". Found: {}'.format(root.tag))

        payload = root[0]
        self._parse_payload(payload)

    @abstractmethod
    def _parse_payload(self, element: Element) -> None:
        """Parse the actual information from the response."""
