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

"""Module providing responses to EPP check commands."""

from dataclasses import dataclass
from typing import ClassVar, Optional, Sequence

from lxml.etree import Element

from epplib.responses.base import NAMESPACES, Result, ResultData, T


class CheckResult(Result[T]):
    """Represents EPP Result which responds to the Check command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str]

    @classmethod
    def _extract_data(cls, element: Optional[Element]) -> Sequence[T]:
        """Extract the content of the resData element.

        Args:
            element: resData epp element.
        """
        data = []
        if element is not None:
            for item in element.findall(cls._res_data_path, namespaces=NAMESPACES):
                item_data = cls._res_data_class.extract(item)
                data.append(item_data)
        return data


@dataclass
class CheckDomainResult(CheckResult):
    """Represents EPP Result which responds to the Check domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Domain(ResultData):
        """Dataclass representing domain availability in the check domain result.

        Attributes:
            name: Content of the epp/response/resData/chkData/cd/name element.
            available: Avail attribute of the epp/response/resData/chkData/cd/name element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        name: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckDomainResult.Domain':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './domain:name'),
                cls._str_to_bool(cls._find_attrib(element, './domain:name', 'avail')),
                cls._find_text(element, './domain:reason'),
            )
            return cls(*params)

    _res_data_path: ClassVar[str] = './domain:chkData/domain:cd'
    _res_data_class: ClassVar = Domain


@dataclass
class CheckContactResult(CheckResult):
    """Represents EPP Result which responds to the Check contact command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Contact(ResultData):
        """Dataclass representing contact availability in the check contact result.

        Attributes:
            id: Content of the epp/response/resData/chkData/cd/id element.
            available: Avail attribute of the epp/response/resData/chkData/cd/id element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        id: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckContactResult.Contact':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './contact:id'),
                cls._str_to_bool(cls._find_attrib(element, './contact:id', 'avail')),
                cls._find_text(element, './contact:reason'),
            )
            return cls(*params)

    _res_data_path = './contact:chkData/contact:cd'
    _res_data_class: ClassVar = Contact


@dataclass
class CheckNssetResult(CheckResult):
    """Represents EPP Result which responds to the Check nsset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Nsset(ResultData):
        """Dataclass representing nsset availability in the check nsset result.

        Attributes:
            id: Content of the epp/response/resData/chkData/cd/id element.
            available: Avail attribute of the epp/response/resData/chkData/cd/id element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        id: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckNssetResult.Nsset':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './nsset:id'),
                cls._str_to_bool(cls._find_attrib(element, './nsset:id', 'avail')),
                cls._find_text(element, './nsset:reason'),
            )
            return cls(*params)

    _res_data_path = './nsset:chkData/nsset:cd'
    _res_data_class: ClassVar = Nsset


@dataclass
class CheckKeysetResult(CheckResult):
    """Represents EPP Result which responds to the Check keyset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Keyset(ResultData):
        """Dataclass representing keyset availability in the check keyset result.

        Attributes:
            id: Content of the epp/response/resData/chkData/cd/id element.
            available: Avail attribute of the epp/response/resData/chkData/cd/id element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        id: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckKeysetResult.Keyset':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './keyset:id'),
                cls._str_to_bool(cls._find_attrib(element, './keyset:id', 'avail')),
                cls._find_text(element, './keyset:reason'),
            )
            return cls(*params)

    _res_data_path = './keyset:chkData/keyset:cd'
    _res_data_class: ClassVar = Keyset
