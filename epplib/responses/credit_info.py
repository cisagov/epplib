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
from decimal import Decimal
from typing import ClassVar

from lxml.etree import Element

from epplib.models import ExtractModelMixin
from epplib.responses.base import Result


@dataclass
class CreditInfoResult(Result):
    """Represents EPP Result which responds to the Check domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        msg: Content of the epp/response/result/msg element.
        res_data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class ZoneCredit(ExtractModelMixin):
        """Dataclass representing zone credit in the credit info result.

        Attributes:
            zone: Content of the epp/response/resData/resCreditInfo/zoneCredit/zone element.
            credit: Content of the epp/response/resData/resCreditInfo/zoneCredit/credit element.
        """

        zone: str
        credit: Decimal

        @classmethod
        def extract(cls, element: Element) -> 'CreditInfoResult.ZoneCredit':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './fred:zone'),
                Decimal(cls._find_text(element, './fred:credit')),
            )
            return cls(*params)

    _res_data_path: ClassVar[str] = './fred:resCreditInfo/fred:zoneCredit'
    _res_data_class: ClassVar = ZoneCredit
