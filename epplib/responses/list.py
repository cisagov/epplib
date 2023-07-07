#
# Copyright (C) 2021-2022  CZ.NIC, z. s. p. o.
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

from epplib.models.list import GetResultsResultData, ListResultData
from epplib.responses.base import Result


@dataclass
class ListResult(Result[ListResultData]):
    """Represents EPP Result which responds to the list command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = "./fred:infoResponse"
    _res_data_class = ListResultData


@dataclass
class GetResultsResult(Result[GetResultsResultData]):
    """Represents EPP Result which responds to the get results command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = "./fred:resultsList/fred:item"
    _res_data_class = GetResultsResultData
