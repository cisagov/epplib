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

"""Module providing responses to EPP credit info command."""

from dataclasses import dataclass
from decimal import Decimal

from lxml.etree import Element

from epplib.models import ExtractModelMixin


@dataclass
class CreditInfoResultData(ExtractModelMixin):
    """Dataclass representing zone credit in the credit info result.

    Attributes:
        zone: Content of the epp/response/resData/resCreditInfo/zoneCredit/zone element.
        credit: Content of the epp/response/resData/resCreditInfo/zoneCredit/credit element.
    """

    zone: str
    credit: Decimal

    @classmethod
    def extract(cls, element: Element) -> 'CreditInfoResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './fred:zone'),
            Decimal(cls._find_text(element, './fred:credit')),
        )
        return cls(*params)
