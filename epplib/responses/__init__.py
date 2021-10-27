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

"""Module providing means to process responses to EPP commands."""

from .base import Greeting, ParsingError, Response, Result, ResultData
from .check import CheckContactResult, CheckDomainResult, CheckKeysetResult, CheckNssetResult
from .create import CreateContactResult, CreateDomainResult, CreateKeysetResult, CreateNssetResult
from .credit_info import CreditInfoResult
from .info import InfoDomainResult
from .list import ListResult
from .renew import RenewDomainResult

__all__ = [
    'CheckContactResult',
    'CheckDomainResult',
    'CheckKeysetResult',
    'CheckNssetResult',
    'CreateContactResult',
    'CreateDomainResult',
    'CreateKeysetResult',
    'CreateNssetResult',
    'CreditInfoResult',
    'Greeting',
    'InfoDomainResult',
    'ListResult',
    'ParsingError',
    'RenewDomainResult',
    'Response',
    'Result',
    'ResultData',
]
