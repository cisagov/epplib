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
from typing import ClassVar, Mapping, Type

from lxml.etree import Element, QName

POLL_MESSAGE_TYPES: Mapping[QName, Type['PollMessage']] = {}


class PollMessage(ABC):
    """Base class for poll messages."""

    tag: ClassVar[QName]

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'PollMessage':
        """Extract the Message from the element."""
