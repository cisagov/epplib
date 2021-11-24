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
from datetime import date, datetime
from typing import ClassVar, Optional

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element

from epplib.models import ExtractModelMixin
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

    @dataclass
    class Domain(ExtractModelMixin):
        """Dataclass representing result of domain creation.

        Attributes:
            name: Content of the epp/response/resData/creData/name element.
            cr_date: Content of the epp/response/resData/creData/crDate element.
            ex_date: Content of the epp/response/resData/creData/exDate element.
        """

        name: str
        cr_date: datetime
        ex_date: Optional[date] = None

        @classmethod
        def extract(cls, element: Element) -> 'CreateDomainResult.Domain':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './domain:name'),
                parse_datetime(cls._find_text(element, './domain:crDate')),
                cls._optional(cls._parse_date, cls._find_text(element, './domain:exDate')),
            )
            return cls(*params)

    _res_data_path: ClassVar[str] = './domain:creData'
    _res_data_class: ClassVar = Domain


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

    @dataclass
    class NonDomain(ExtractModelMixin):
        """Dataclass representing result of creation of object other than domain.

        Attributes:
            id: Content of the epp/response/resData/creData/id element.
            cr_date: Content of the epp/response/resData/creData/crDate element.
        """

        id: str
        cr_date: datetime

        _namespace_prefix: ClassVar[Optional[str]] = None

        @classmethod
        def extract(cls, element: Element) -> 'CreateNonDomainResult.NonDomain':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './{}:id'.format(cls._namespace_prefix)),
                parse_datetime(cls._find_text(element, './{}:crDate'.format(cls._namespace_prefix))),
            )
            return cls(*params)

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

    @dataclass
    class Contact(CreateNonDomainResult.NonDomain):
        """Dataclass representing result of contact creation.

        Attributes:
            id: Content of the epp/response/resData/creData/id element.
            cr_date: Content of the epp/response/resData/creData/crDate element.
        """

        _namespace_prefix: ClassVar[Optional[str]] = 'contact'

    _namespace_prefix: ClassVar[Optional[str]] = 'contact'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = Contact


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

    @dataclass
    class Nsset(CreateNonDomainResult.NonDomain):
        """Dataclass representing result of nsset creation.

        Attributes:
            id: Content of the epp/response/resData/creData/id element.
            cr_date: Content of the epp/response/resData/creData/crDate element.
        """

        _namespace_prefix: ClassVar[Optional[str]] = 'nsset'

    _namespace_prefix: ClassVar[Optional[str]] = 'nsset'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = Nsset


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

    @dataclass
    class Keyset(CreateNonDomainResult.NonDomain):
        """Dataclass representing result of keyset creation.

        Attributes:
            id: Content of the epp/response/resData/creData/id element.
            cr_date: Content of the epp/response/resData/creData/crDate element.
        """

        _namespace_prefix: ClassVar[Optional[str]] = 'keyset'

    _namespace_prefix: ClassVar[Optional[str]] = 'keyset'
    _res_data_path: ClassVar[str] = './{}:creData'.format(_namespace_prefix)
    _res_data_class: ClassVar = Keyset
