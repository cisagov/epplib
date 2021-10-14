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

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, ClassVar, List, Optional, Tuple

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element

from epplib.models import Status
from epplib.responses.base import Result, ResultData


@dataclass
class InfoDomainResult(Result):
    """Represents EPP Result which responds to the Info domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Domain(ResultData):
        """Dataclass representing domain info in the info domain result.

        Attributes:
            name: Content of the epp/response/resData/infData/name element.
            roid: Content of the epp/response/resData/infData/roid element.
            statuses: Content of the epp/response/resData/infData/status element.
            cl_id: Content of the epp/response/resData/infData/clID element.
            registrant: Content of the epp/response/resData/infData/registrant element.
            admins: Content of the epp/response/resData/infData/admin element.
            nsset: Content of the epp/response/resData/infData/nsset element.
            keyset: Content of the epp/response/resData/infData/keyset element.
            cr_id: Content of the epp/response/resData/infData/crID element.
            cr_date: Content of the epp/response/resData/infData/crDate element.
            up_id: Content of the epp/response/resData/infData/upID element.
            up_date: Content of the epp/response/resData/infData/upDate element.
            ex_date: Content of the epp/response/resData/infData/exDate element.
            tr_date: Content of the epp/response/resData/infData/trDate element.
            auth_info: Content of the epp/response/resData/infData/authInfo element.
        """

        name: str
        roid: str
        statuses: List[Status]
        cl_id: str
        registrant: Optional[str]
        admins: List[str] = field(default_factory=list)
        nsset: Optional[str] = None
        keyset: Optional[str] = None
        cr_id: Optional[str] = None
        cr_date: Optional[datetime] = None
        up_id: Optional[str] = None
        up_date: Optional[datetime] = None
        ex_date: Optional[date] = None
        tr_date: Optional[datetime] = None
        auth_info: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'InfoDomainResult.Domain':
            """Extract params for own init from the element."""
            params: Tuple[Any, ...] = (
                cls._find_text(element, './domain:name'),
                cls._find_text(element, './domain:roid'),
                cls._parse_statuses(cls._find_all(element, './domain:status')),
                cls._find_text(element, './domain:clID'),
                cls._find_text(element, './domain:registrant'),
                cls._find_all_text(element, './domain:admin'),
                cls._find_text(element, './domain:nsset'),
                cls._find_text(element, './domain:keyset'),
                cls._find_text(element, './domain:crID'),
                cls._optional(parse_datetime, cls._find_text(element, './domain:crDate')),
                cls._find_text(element, './domain:upID'),
                cls._optional(parse_datetime, cls._find_text(element, './domain:upDate')),
                cls._optional(cls._parse_date, cls._find_text(element, './domain:exDate')),
                cls._optional(parse_datetime, cls._find_text(element, './domain:trDate')),
                cls._find_text(element, './domain:authInfo'),
            )
            return cls(*params)

        @classmethod
        def _parse_statuses(cls, elements: List[Element]) -> List[Status]:
            return [Status(item.get('s'), item.text, item.get('lang')) for item in elements]

    _res_data_path: ClassVar[str] = './domain:infData'
    _res_data_class: ClassVar = Domain
