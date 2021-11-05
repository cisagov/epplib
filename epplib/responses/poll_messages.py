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
from decimal import Decimal
from typing import ClassVar, Mapping, Type

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


POLL_MESSAGE_TYPES: Mapping[QName, Type['PollMessage']] = {
    LowCredit.tag: LowCredit,
}
