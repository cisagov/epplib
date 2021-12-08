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

"""Module providing responses to EPP create commands."""

from dataclasses import dataclass
from typing import ClassVar, Optional

from epplib.models.create import (CreateContactResultData, CreateDomainResultData, CreateKeysetResultData,
                                  CreateNssetResultData)
from epplib.responses.base import Result


@dataclass
class CreateDomainResult(Result):
    """Represents EPP Result which responds to the create domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str] = './domain:creData'
    _res_data_class: ClassVar = CreateDomainResultData


@dataclass
class CreateNonDomainResult(Result):
    """Represents EPP Result which responds to the create command for objects other than domain.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = None
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = None


@dataclass
class CreateContactResult(CreateNonDomainResult):
    """Represents EPP Result which responds to the create contact command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'contact'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = CreateContactResultData


@dataclass
class CreateNssetResult(CreateNonDomainResult):
    """Represents EPP Result which responds to the create nsset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'nsset'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = CreateNssetResultData


@dataclass
class CreateKeysetResult(CreateNonDomainResult):
    """Represents EPP Result which responds to the create keyset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _namespace_prefix: ClassVar[Optional[str]] = 'keyset'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = CreateKeysetResultData
