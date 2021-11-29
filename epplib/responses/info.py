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
from typing import ClassVar

from epplib.models.info import InfoContactResultData, InfoDomainResultData, InfoKeysetResultData, InfoNssetResultData
from epplib.responses.base import Result


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

    _res_data_path: ClassVar[str] = './domain:infData'
    _res_data_class: ClassVar = InfoDomainResultData


@dataclass
class InfoContactResult(Result):
    """Represents EPP Result which responds to the Info contact command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str] = './contact:infData'
    _res_data_class: ClassVar = InfoContactResultData


@dataclass
class InfoKeysetResult(Result):
    """Represents EPP Result which responds to the Info keyset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str] = './keyset:infData'
    _res_data_class: ClassVar = InfoKeysetResultData


@dataclass
class InfoNssetResult(Result):
    """Represents EPP Result which responds to the Info nsset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str] = './nsset:infData'
    _res_data_class: ClassVar = InfoNssetResultData
