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

"""Module providing responses to EPP list commands."""

from dataclasses import dataclass
from typing import ClassVar

from lxml.etree import Element

from epplib.responses.base import Result, ResultData


@dataclass
class ListResult(Result):
    """Represents EPP Result which responds to the list command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class InfoResponse(ResultData):
        """Dataclass representing the list command result.

        Attributes:
            count: Content of the epp/response/resData/infoResponse/count element.
        """

        count: int

        @classmethod
        def extract(cls, element: Element) -> 'ListResult.InfoResponse':
            """Extract params for own init from the element."""
            count = int(cls._find_text(element, './fred:count'))
            return cls(count=count)

    _res_data_path: ClassVar[str] = './fred:infoResponse'
    _res_data_class: ClassVar = InfoResponse
