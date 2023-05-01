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

"""Module providing models to EPP check responses."""

from dataclasses import dataclass
from typing import Optional

from lxml.etree import Element

from epplib.models import ExtractModelMixin


@dataclass
class CheckDomainResultData(ExtractModelMixin):
    """Dataclass representing domain availability in the check domain result.

    Attributes:
        name: Content of the epp/response/resData/chkData/cd/name element.
        avail: Avail attribute of the epp/response/resData/chkData/cd/name element.
        reason: Content of the epp/response/resData/chkData/cd/reason element.
    """

    name: str
    avail: Optional[bool]
    reason: Optional[str] = None

    @classmethod
    def extract(cls, element: Element) -> 'CheckDomainResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './domain:name'),
            cls._str_to_bool(cls._find_attrib(element, './domain:name', 'avail')),
            cls._find_text(element, './domain:reason'),
        )
        return cls(*params)


@dataclass
class CheckContactResultData(ExtractModelMixin):
    """Dataclass representing contact availability in the check contact result.

    Attributes:
        id: Content of the epp/response/resData/chkData/cd/id element.
        avail: Avail attribute of the epp/response/resData/chkData/cd/id element.
        reason: Content of the epp/response/resData/chkData/cd/reason element.
    """

    id: str
    avail: Optional[bool]
    reason: Optional[str] = None

    @classmethod
    def extract(cls, element: Element) -> 'CheckContactResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './contact:id'),
            cls._str_to_bool(cls._find_attrib(element, './contact:id', 'avail')),
            cls._find_text(element, './contact:reason'),
        )
        return cls(*params)


@dataclass
class CheckHostResultData(ExtractModelMixin):
    """Dataclass representing host availability in the check host result.

    Attributes:
        name: Content of the epp/response/resData/chkData/cd/name element.
        avail: Avail attribute of the epp/response/resData/chkData/cd/name element.
        reason: Content of the epp/response/resData/chkData/cd/reason element.
    """

    name: str
    avail: Optional[bool]
    reason: Optional[str] = None

    @classmethod
    def extract(cls, element: Element) -> 'CheckHostResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './host:name'),
            cls._str_to_bool(cls._find_attrib(element, './host:name', 'avail')),
            cls._find_text(element, './host:reason'),
        )
        return cls(*params)


@dataclass
class CheckNssetResultData(ExtractModelMixin):
    """Dataclass representing nsset availability in the check nsset result.

    Attributes:
        id: Content of the epp/response/resData/chkData/cd/id element.
        avail: Avail attribute of the epp/response/resData/chkData/cd/id element.
        reason: Content of the epp/response/resData/chkData/cd/reason element.
    """

    id: str
    avail: Optional[bool]
    reason: Optional[str] = None

    @classmethod
    def extract(cls, element: Element) -> 'CheckNssetResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './nsset:id'),
            cls._str_to_bool(cls._find_attrib(element, './nsset:id', 'avail')),
            cls._find_text(element, './nsset:reason'),
        )
        return cls(*params)


@dataclass
class CheckKeysetResultData(ExtractModelMixin):
    """Dataclass representing keyset availability in the check keyset result.

    Attributes:
        id: Content of the epp/response/resData/chkData/cd/id element.
        avail: Avail attribute of the epp/response/resData/chkData/cd/id element.
        reason: Content of the epp/response/resData/chkData/cd/reason element.
    """

    id: str
    avail: Optional[bool]
    reason: Optional[str] = None

    @classmethod
    def extract(cls, element: Element) -> 'CheckKeysetResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './keyset:id'),
            cls._str_to_bool(cls._find_attrib(element, './keyset:id', 'avail')),
            cls._find_text(element, './keyset:reason'),
        )
        return cls(*params)
