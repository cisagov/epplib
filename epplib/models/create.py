#
# Copyright (C) 2021-2023  CZ.NIC, z. s. p. o.
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
#
"""Module providing models for EPP create responses."""
from dataclasses import MISSING, dataclass
from datetime import date, datetime
from typing import ClassVar, Optional

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element

from epplib.models import ContactAddr, ExtractModelMixin, PostalInfo


@dataclass
class CreatePostalInfo(PostalInfo):
    """Dataclass to represent EPP postalInfo element in contact creation."""

    # Name and addr is required in contact create.
    # We need to explicitely set defaults to MISSING to override defaults from PostalInfo.
    name: str = MISSING  # type: ignore[assignment]
    addr: ContactAddr = MISSING  # type: ignore[assignment]


@dataclass
class CreateDomainResultData(ExtractModelMixin):
    """Dataclass representing result of domain creation.

    Attributes:
        name: Content of the epp/response/resData/creData/name element.
        cr_date: Content of the epp/response/resData/creData/crDate element.
        ex_date: Content of the epp/response/resData/creData/exDate element.
    """

    name: str
    cr_date: datetime
    ex_date: Optional[date] = None

    @classmethod
    def extract(cls, element: Element) -> 'CreateDomainResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './domain:name'),
            parse_datetime(cls._find_text(element, './domain:crDate')),
            cls._optional(cls._parse_date, cls._find_text(element, './domain:exDate')),
        )
        return cls(*params)


@dataclass
class CreateNonDomainResultData(ExtractModelMixin):
    """Dataclass representing result of creation of object other than domain.

    Attributes:
        id: Content of the epp/response/resData/creData/id element.
        cr_date: Content of the epp/response/resData/creData/crDate element.
    """

    id: str
    cr_date: datetime

    _namespace_prefix: ClassVar[Optional[str]] = None

    @classmethod
    def extract(cls, element: Element) -> 'CreateNonDomainResultData':
        """Extract params for own init from the element."""
        params = (
            cls._find_text(element, './{}:id'.format(cls._namespace_prefix)),
            parse_datetime(cls._find_text(element, './{}:crDate'.format(cls._namespace_prefix))),
        )
        return cls(*params)


@dataclass
class CreateContactResultData(CreateNonDomainResultData):
    """Dataclass representing result of contact creation.

    Attributes:
        id: Content of the epp/response/resData/creData/id element.
        cr_date: Content of the epp/response/resData/creData/crDate element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'contact'


@dataclass
class CreateNssetResultData(CreateNonDomainResultData):
    """Dataclass representing result of nsset creation.

    Attributes:
        id: Content of the epp/response/resData/creData/id element.
        cr_date: Content of the epp/response/resData/creData/crDate element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'nsset'


@dataclass
class CreateKeysetResultData(CreateNonDomainResultData):
    """Dataclass representing result of keyset creation.

    Attributes:
        id: Content of the epp/response/resData/creData/id element.
        cr_date: Content of the epp/response/resData/creData/crDate element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'keyset'
