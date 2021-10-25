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
from datetime import date, datetime
from typing import Any, ClassVar, List, Mapping, Optional

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element

from epplib.models import Status
from epplib.responses.base import Result, ResultData


@dataclass
class InfoResult(Result):
    """Represents EPP Result which responds to the Info command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Item(ResultData):
        """Dataclass representing queried item info in the info result.

        Attributes:
            roid: Content of the epp/response/resData/infData/roid element.
            statuses: Content of the epp/response/resData/infData/status element.
            cl_id: Content of the epp/response/resData/infData/clID element.
            cr_id: Content of the epp/response/resData/infData/crID element.
            cr_date: Content of the epp/response/resData/infData/crDate element.
            up_id: Content of the epp/response/resData/infData/upID element.
            up_date: Content of the epp/response/resData/infData/upDate element.
            tr_date: Content of the epp/response/resData/infData/trDate element.
            auth_info: Content of the epp/response/resData/infData/authInfo element.
        """

        _namespace: ClassVar[str]

        roid: str
        statuses: List[Status]
        cl_id: str
        cr_id: Optional[str]
        cr_date: Optional[datetime]
        up_id: Optional[str]
        up_date: Optional[datetime]
        tr_date: Optional[datetime]
        auth_info: Optional[str]

        @classmethod
        def extract(cls, element: Element) -> 'InfoResult.Item':
            """Extract params for own init from the element."""
            return cls(**cls._get_params(element))

        @classmethod
        def _get_params(cls, element: Element) -> Mapping[str, Any]:
            params: Mapping[str, Any] = {
                'roid': cls._find_text(element, f'./{cls._namespace}:roid'),
                'statuses': [Status.extract(item) for item in cls._find_all(element, f'./{cls._namespace}:status')],
                'cl_id': cls._find_text(element, f'./{cls._namespace}:clID'),
                'cr_id': cls._find_text(element, f'./{cls._namespace}:crID'),
                'cr_date': cls._optional(parse_datetime, cls._find_text(element, f'./{cls._namespace}:crDate')),
                'up_id': cls._find_text(element, f'./{cls._namespace}:upID'),
                'up_date': cls._optional(parse_datetime, cls._find_text(element, f'./{cls._namespace}:upDate')),
                'tr_date': cls._optional(parse_datetime, cls._find_text(element, f'./{cls._namespace}:trDate')),
                'auth_info': cls._find_text(element, f'./{cls._namespace}:authInfo'),
            }
            return params


@dataclass
class InfoDomainResult(InfoResult):
    """Represents EPP Result which responds to the Info domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Domain(InfoResult.Item):
        """Dataclass representing domain info in the info domain result.

        Attributes:
            cl_id: Content of the epp/response/resData/infData/clID element.
            cr_id: Content of the epp/response/resData/infData/crID element.
            cr_date: Content of the epp/response/resData/infData/crDate element.
            up_id: Content of the epp/response/resData/infData/upID element.
            up_date: Content of the epp/response/resData/infData/upDate element.
            tr_date: Content of the epp/response/resData/infData/trDate element.
            auth_info: Content of the epp/response/resData/infData/authInfo element.
            name: Content of the epp/response/resData/infData/name element.
            registrant: Content of the epp/response/resData/infData/registrant element.
            admins: Content of the epp/response/resData/infData/admin element.
            nsset: Content of the epp/response/resData/infData/nsset element.
            keyset: Content of the epp/response/resData/infData/keyset element.
            ex_date: Content of the epp/response/resData/infData/exDate element.
        """

        _namespace = 'domain'

        name: str
        registrant: Optional[str]
        admins: List[str]
        nsset: Optional[str]
        keyset: Optional[str]
        ex_date: Optional[date]

        @classmethod
        def _get_params(cls, element: Element) -> Mapping[str, Any]:
            params: Mapping[str, Any] = {
                'name': cls._find_text(element, f'./{cls._namespace}:name'),
                'registrant': cls._find_text(element, f'./{cls._namespace}:registrant'),
                'admins': cls._find_all_text(element, f'./{cls._namespace}:admin'),
                'nsset': cls._find_text(element, f'./{cls._namespace}:nsset'),
                'keyset': cls._find_text(element, f'./{cls._namespace}:keyset'),
                'ex_date': cls._optional(cls._parse_date, cls._find_text(element, f'./{cls._namespace}:exDate')),
            }
            return {**super()._get_params(element), **params}

    _res_data_path: ClassVar[str] = './domain:infData'
    _res_data_class: ClassVar = Domain
