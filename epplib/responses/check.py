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

"""Module providing responses to EPP check commands."""

from dataclasses import dataclass

from epplib.models.check import (CheckContactResultData, CheckDomainResultData, CheckHostResultData,
                                 CheckKeysetResultData, CheckNssetResultData)
from epplib.responses.base import Result


@dataclass
class CheckDomainResult(Result[CheckDomainResultData]):
    """Represents EPP Result which responds to the Check domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = './domain:chkData/domain:cd'
    _res_data_class = CheckDomainResultData


@dataclass
class CheckContactResult(Result[CheckContactResultData]):
    """Represents EPP Result which responds to the Check contact command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = './contact:chkData/contact:cd'
    _res_data_class = CheckContactResultData


@dataclass
class CheckHostResult(Result[CheckHostResultData]):
    """Represents EPP Result which responds to the Check host command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = './host:chkData/host:cd'
    _res_data_class = CheckHostResultData


@dataclass
class CheckNssetResult(Result[CheckNssetResultData]):
    """Represents EPP Result which responds to the Check nsset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = './nsset:chkData/nsset:cd'
    _res_data_class = CheckNssetResultData


@dataclass
class CheckKeysetResult(Result[CheckKeysetResultData]):
    """Represents EPP Result which responds to the Check keyset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path = './keyset:chkData/keyset:cd'
    _res_data_class = CheckKeysetResultData
