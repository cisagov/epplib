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

"""Module providing base classes to EPP command responses."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Statement:
    """A dataclass to represent the EPP statement.

    Attributes:
        purpose: Content of the epp/greeting/statement/purpose element.
        recipient: Content of the epp/greeting/statement/recipient element.
        retention: Content of the epp/greeting/statement/retention element.
    """

    purpose: List[str]
    recipient: List[str]
    retention: Optional[str]


@dataclass
class Status:
    """Represents a status of the queried object in the InfoResult."""

    state: str
    description: str
    lang: Optional[str] = None

    def __post_init__(self):
        if self.lang is None:
            self.lang = 'en'
