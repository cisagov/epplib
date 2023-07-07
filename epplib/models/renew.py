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

"""Module providing models to EPP renew responses."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from lxml.etree import Element

from epplib.models import ExtractModelMixin


@dataclass
class RenewDomainResultData(ExtractModelMixin):
    """Dataclass representing domain availability in the renew domain result.

    Attributes:
        name: Content of the epp/response/resData/renData/name element.
        ex_date: Avail attribute of the epp/response/resData/renData//name element.
    """

    name: str
    ex_date: Optional[date]

    @classmethod
    def extract(cls, element: Element) -> "RenewDomainResultData":
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, "./domain:name"),
            cls._optional(cls._parse_date, cls._find_text(element, "./domain:exDate")),
        )
        return cls(*params)
