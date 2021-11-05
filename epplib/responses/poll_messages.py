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

"""Module providing classes for EPP poll messages."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import ClassVar, Mapping, Type

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element, QName

from epplib.constants import NAMESPACE
from epplib.utils import ParseXMLMixin


class PollMessage(ABC):
    """Base class for poll messages."""

    tag: ClassVar[QName]

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'PollMessage':
        """Extract the Message from the element."""


@dataclass
class LowCredit(ParseXMLMixin, PollMessage):
    """Low credit poll message."""

    tag = QName(NAMESPACE.FRED, 'lowCreditData')

    zone: str
    limit_zone: str
    limit: Decimal
    credit_zone: str
    credit: Decimal

    @classmethod
    def extract(cls, element: Element) -> 'LowCredit':
        """Extract the Message from the element."""
        zone = cls._find_text(element, './fred:zone')
        credit_zone = cls._find_text(element, './fred:credit/fred:zone')
        credit = Decimal(cls._find_text(element, './fred:credit/fred:credit'))
        limit_zone = cls._find_text(element, './fred:limit/fred:zone')
        limit = Decimal(cls._find_text(element, './fred:limit/fred:credit'))
        return cls(zone=zone, credit_zone=credit_zone, credit=credit, limit_zone=limit_zone, limit=limit)


@dataclass
class RequestUsage(ParseXMLMixin, PollMessage):
    """Request usage poll message."""

    tag = QName(NAMESPACE.FRED, 'requestFeeInfoData')

    period_from: datetime
    period_to: datetime
    total_free_count: int
    used_count: int
    price: Decimal

    @classmethod
    def extract(cls, element: Element) -> 'RequestUsage':
        """Extract the Message from the element."""
        period_from = parse_datetime(cls._find_text(element, './fred:periodFrom'))
        period_to = parse_datetime(cls._find_text(element, './fred:periodTo'))
        total_free_count = int(cls._find_text(element, './fred:totalFreeCount'))
        used_count = int(cls._find_text(element, './fred:usedCount'))
        price = Decimal(cls._find_text(element, './fred:price'))
        return cls(
            period_from=period_from,
            period_to=period_to,
            total_free_count=total_free_count,
            used_count=used_count,
            price=price,
        )


POLL_MESSAGE_TYPES: Mapping[QName, Type['PollMessage']] = {
    LowCredit.tag: LowCredit,
    RequestUsage.tag: RequestUsage,
}
