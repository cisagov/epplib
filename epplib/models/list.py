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

"""Module providing models to EPP list responses."""

from dataclasses import dataclass

from lxml.etree import Element

from epplib.models import ExtractModelMixin


@dataclass
class ListResultData(ExtractModelMixin):
    """Dataclass representing the list command result.

    Attributes:
        count: Content of the epp/response/resData/infoResponse/count element.
    """

    count: int

    @classmethod
    def extract(cls, element: Element) -> 'ListResultData':
        """Extract params for own init from the element."""
        count = int(cls._find_text(element, './fred:count'))
        return cls(count=count)


class GetResultsResultData(ExtractModelMixin, str):
    """Class representing the list command result."""

    @classmethod
    def extract(cls, element: Element) -> 'GetResultsResultData':
        """Extract params for own init from the element."""
        value = cls._find_text(element, '.')
        return cls(value)
