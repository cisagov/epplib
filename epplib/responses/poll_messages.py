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

"""Module providing classes for EPP poll messages."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar, Generic, Mapping, Sequence, Type, TypeVar, cast

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element, QName

from epplib.constants import NAMESPACE
from epplib.models import TestResult
from epplib.models.info import (InfoContactResultData, InfoDomainResultData, InfoKeysetResultData, InfoNssetResultData,
                                InfoResultData)
from epplib.utils import ParseXMLMixin

T = TypeVar('T', bound=InfoResultData)
ObjectUpdateT = TypeVar('ObjectUpdateT', bound='ObjectUpdate')


class PollMessage(ABC):
    """Base class for poll messages."""

    tag: ClassVar[QName]

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'PollMessage':
        """Extract the Message from the element."""


@dataclass
class LowCredit(ParseXMLMixin, PollMessage):
    """Low credit poll message.

    Attributes:
        zone: Content of the epp/response/msgQ/msg/lowCreditData/zone element.
        limit_zone: Content of the epp/response/msgQ/msg/lowCreditData/limit/zone element.
        limit: Content of the epp/response/msgQ/msg/lowCreditData/limit/credit element.
        credit_zone: Content of the epp/response/msgQ/msg/lowCreditData/credit/zone element.
        credit: Content of the epp/response/msgQ/msg/lowCreditData/credit/credit element.
    """

    tag = QName(NAMESPACE.FRED, 'lowCreditData')

    zone: str
    limit_zone: str
    limit: Decimal
    credit_zone: str
    credit: Decimal

    @classmethod
    def extract(cls, element: Element) -> 'LowCredit':
        """Extract the Message from the element."""
        zone = cls._find_text(element, './fred:zone')
        credit_zone = cls._find_text(element, './fred:credit/fred:zone')
        credit = Decimal(cls._find_text(element, './fred:credit/fred:credit'))
        limit_zone = cls._find_text(element, './fred:limit/fred:zone')
        limit = Decimal(cls._find_text(element, './fred:limit/fred:credit'))
        return cls(zone=zone, credit_zone=credit_zone, credit=credit, limit_zone=limit_zone, limit=limit)


@dataclass
class RequestUsage(ParseXMLMixin, PollMessage):
    """Request usage poll message.

    Attributes:
        period_from: Content of the epp/response/msgQ/msg/requestFeeInfoData/periodFrom element.
        period_to: Content of the epp/response/msgQ/msg/requestFeeInfoData/periodTo element.
        total_free_count: Content of the epp/response/msgQ/msg/requestFeeInfoData/totalFreeCount element.
        used_count: Content of the epp/response/msgQ/msg/requestFeeInfoData/usedCount element.
        price: Content of the epp/response/msgQ/msg/requestFeeInfoData/price element.
    """

    tag = QName(NAMESPACE.FRED, 'requestFeeInfoData')

    period_from: datetime
    period_to: datetime
    total_free_count: int
    used_count: int
    price: Decimal

    @classmethod
    def extract(cls, element: Element) -> 'RequestUsage':
        """Extract the Message from the element."""
        period_from = parse_datetime(cls._find_text(element, './fred:periodFrom'))
        period_to = parse_datetime(cls._find_text(element, './fred:periodTo'))
        total_free_count = int(cls._find_text(element, './fred:totalFreeCount'))
        used_count = int(cls._find_text(element, './fred:usedCount'))
        price = Decimal(cls._find_text(element, './fred:price'))
        return cls(
            period_from=period_from,
            period_to=period_to,
            total_free_count=total_free_count,
            used_count=used_count,
            price=price,
        )


@dataclass
class DomainExpiration(ParseXMLMixin, PollMessage):
    """Domain expiration poll message.

    Attributes:
        name: Content of the epp/response/msgQ/msg/*/name element.
        ex_date: Content of the epp/response/msgQ/msg/*/exDate element.
    """

    name: str
    ex_date: date

    @classmethod
    def extract(cls, element: Element) -> 'DomainExpiration':
        """Extract the Message from the element."""
        name = cls._find_text(element, './domain:name')
        ex_date = cls._parse_date(cls._find_text(element, './domain:exDate'))
        return cls(name=name, ex_date=ex_date)


@dataclass
class ImpendingExpData(DomainExpiration):
    """Impending Exp Data poll message."""

    tag = 'impendingExpData'


@dataclass
class ExpData(DomainExpiration):
    """Exp Data poll message."""

    tag = 'expData'


@dataclass
class DnsOutageData(DomainExpiration):
    """Dns Outage Data poll message."""

    tag = 'dnsOutageData'


@dataclass
class DelData(DomainExpiration):
    """Del Data poll message."""

    tag = 'delData'


@dataclass
class DomainValidation(ParseXMLMixin, PollMessage):
    """Domain validation poll message.

    Attributes:
        name: Content of the epp/response/msgQ/msg/*/name element.
        val_ex_date: Content of the epp/response/msgQ/msg/*/valExDate element.
    """

    _NAMESPACES = {
        **ParseXMLMixin._NAMESPACES,
        'enumval': NAMESPACE.NIC_ENUMVAL,
    }

    name: str
    val_ex_date: date

    @classmethod
    def extract(cls, element: Element) -> 'DomainValidation':
        """Extract the Message from the element."""
        name = cls._find_text(element, './enumval:name')
        val_ex_date = cls._parse_date(cls._find_text(element, './enumval:valExDate'))
        return cls(name=name, val_ex_date=val_ex_date)


@dataclass
class ImpendingValExpData(DomainValidation):
    """Impending Val Exp Data poll message."""

    tag = QName(NAMESPACE.NIC_ENUMVAL, 'impendingValExpData')


@dataclass
class ValExpData(DomainValidation):
    """Val Exp Data poll message."""

    tag = QName(NAMESPACE.NIC_ENUMVAL, 'valExpData')


class ObjectTransfer(ParseXMLMixin, PollMessage):
    """Object transfer poll message.

    Attributes:
        tr_date: Content of the epp/response/msgQ/msg/trnData/tr_date element.
        cl_id: Content of the epp/response/msgQ/msg/trnData/clID element.
    """

    _prefix: ClassVar[str]

    tr_date: date
    cl_id: str

    @classmethod
    def _extract(cls, element: Element) -> Mapping[str, Any]:
        """Extract the Message from the element."""
        return {
            'tr_date': cls._parse_date(cls._find_text(element, f'./{cls._prefix}:trDate')),
            'cl_id': cls._find_text(element, f'./{cls._prefix}:clID'),
        }


@dataclass
class DomainTransfer(ObjectTransfer):
    """Domain transfer poll message.

    Attributes:
        name: Content of the epp/response/msgQ/msg/trnData/name element.
        tr_date: Content of the epp/response/msgQ/msg/trnData/tr_date element.
        cl_id: Content of the epp/response/msgQ/msg/trnData/clID element.
    """

    _prefix = 'domain'
    tag = QName(NAMESPACE.NIC_DOMAIN, 'trnData')
    name: str
    tr_date: date
    cl_id: str

    @classmethod
    def extract(cls, element: Element) -> 'DomainTransfer':
        """Extract the Message from the element."""
        data = cls._extract(element)
        data = {
            **data,
            'name': cls._find_text(element, f'./{cls._prefix}:name'),
        }
        return cls(**data)


@dataclass
class ContactTransfer(ObjectTransfer):
    """Contact transfer poll message.

    Attributes:
        id: Content of the epp/response/msgQ/msg/trnData/id element.
        tr_date: Content of the epp/response/msgQ/msg/trnData/tr_date element.
        cl_id: Content of the epp/response/msgQ/msg/trnData/clID element.
    """

    _prefix = 'contact'
    tag = QName(NAMESPACE.NIC_CONTACT, 'trnData')
    id: str
    tr_date: date
    cl_id: str

    @classmethod
    def extract(cls, element: Element) -> 'ContactTransfer':
        """Extract the Message from the element."""
        data = cls._extract(element)
        data = {
            **data,
            'id': cls._find_text(element, f'./{cls._prefix}:id'),
        }
        return cls(**data)


@dataclass
class KeysetTransfer(ObjectTransfer):
    """Keyset transfer poll message.

    Attributes:
        id: Content of the epp/response/msgQ/msg/trnData/id element.
        tr_date: Content of the epp/response/msgQ/msg/trnData/tr_date element.
        cl_id: Content of the epp/response/msgQ/msg/trnData/clID element.
    """

    _prefix = 'keyset'
    tag = QName(NAMESPACE.NIC_KEYSET, 'trnData')
    id: str
    tr_date: date
    cl_id: str

    @classmethod
    def extract(cls, element: Element) -> 'KeysetTransfer':
        """Extract the Message from the element."""
        data = cls._extract(element)
        data = {
            **data,
            'id': cls._find_text(element, f'./{cls._prefix}:id'),
        }
        return cls(**data)


@dataclass
class NssetTransfer(ObjectTransfer):
    """Nsset transfer poll message.

    Attributes:
        id: Content of the epp/response/msgQ/msg/trnData/id element.
        tr_date: Content of the epp/response/msgQ/msg/trnData/tr_date element.
        cl_id: Content of the epp/response/msgQ/msg/trnData/clID element.
    """

    _prefix = 'nsset'
    tag = QName(NAMESPACE.NIC_NSSET, 'trnData')
    id: str
    tr_date: date
    cl_id: str

    @classmethod
    def extract(cls, element: Element) -> 'NssetTransfer':
        """Extract the Message from the element."""
        data = cls._extract(element)
        data = {
            **data,
            'id': cls._find_text(element, f'./{cls._prefix}:id'),
        }
        return cls(**data)


@dataclass
class ObjectUpdate(ParseXMLMixin, PollMessage, Generic[T]):
    """Object update poll message.

    Attributes:
        op_trid: Content of the epp/response/msgQ/msg/updateData/opTRID element.
        old_data: Content of the epp/response/msgQ/msg/updateData/oldData element.
        new_data: Content of the epp/response/msgQ/msg/updateData/newData element.
    """

    _prefix: ClassVar[str]
    _inf_data_cls: ClassVar[Type[InfoResultData]]

    op_trid: str
    old_data: T
    new_data: T

    @classmethod
    def extract(cls: Type[ObjectUpdateT], element: Element) -> ObjectUpdateT:
        """Extract the Message from the element."""
        op_trid = cls._find_text(element, f'./{cls._prefix}:opTRID')
        old_data = cls._inf_data_cls.extract(cls._find(element, f'./{cls._prefix}:oldData/{cls._prefix}:infData'))
        new_data = cls._inf_data_cls.extract(cls._find(element, f'./{cls._prefix}:newData/{cls._prefix}:infData'))
        return cls(op_trid=op_trid, old_data=cast(T, old_data), new_data=cast(T, new_data))


@dataclass
class DomainUpdate(ObjectUpdate[InfoDomainResultData]):
    """Domain update poll message."""

    _prefix = 'domain'
    _inf_data_cls = InfoDomainResultData

    tag = QName(NAMESPACE.NIC_DOMAIN, 'updateData')


@dataclass
class ContactUpdate(ObjectUpdate[InfoContactResultData]):
    """Contact update poll message."""

    _prefix = 'contact'
    _inf_data_cls = InfoContactResultData

    tag = QName(NAMESPACE.NIC_CONTACT, 'updateData')


@dataclass
class KeysetUpdate(ObjectUpdate[InfoKeysetResultData]):
    """Keyset update poll message."""

    _prefix = 'keyset'
    _inf_data_cls = InfoKeysetResultData

    tag = QName(NAMESPACE.NIC_KEYSET, 'updateData')


@dataclass
class NssetUpdate(ObjectUpdate[InfoNssetResultData]):
    """Nsset update poll message."""

    _prefix = 'nsset'
    _inf_data_cls = InfoNssetResultData

    tag = QName(NAMESPACE.NIC_NSSET, 'updateData')


@dataclass
class IdleObjectDeletion(ParseXMLMixin, PollMessage):
    """Idle object deletion poll message.

    Attributes:
        id: Content of the epp/response/msgQ/msg/idleDelData/id element.
    """

    _prefix: ClassVar[str]

    id: str

    @classmethod
    def extract(cls, element: Element) -> 'IdleObjectDeletion':
        """Extract the Message from the element."""
        return cls(id=cls._find_text(element, f'./{cls._prefix}:id'))


@dataclass
class IdleContactDeletion(IdleObjectDeletion):
    """Idle contact deletion poll message."""

    _prefix = 'contact'
    tag = QName(NAMESPACE.NIC_CONTACT, 'idleDelData')

    @classmethod
    def extract(cls, element: Element) -> 'IdleContactDeletion':
        """Extract the Message from the element."""
        return cast('IdleContactDeletion', super().extract(element))


@dataclass
class IdleKeysetDeletion(IdleObjectDeletion):
    """Idle keyset deletion poll message."""

    _prefix = 'keyset'
    tag = QName(NAMESPACE.NIC_KEYSET, 'idleDelData')

    @classmethod
    def extract(cls, element: Element) -> 'IdleKeysetDeletion':
        """Extract the Message from the element."""
        return cast('IdleKeysetDeletion', super().extract(element))


@dataclass
class IdleNssetDeletion(IdleObjectDeletion):
    """Idle nsset deletion poll message."""

    _prefix = 'nsset'
    tag = QName(NAMESPACE.NIC_NSSET, 'idleDelData')

    @classmethod
    def extract(cls, element: Element) -> 'IdleNssetDeletion':
        """Extract the Message from the element."""
        return cast('IdleNssetDeletion', super().extract(element))


@dataclass
class DomainDeletion(ParseXMLMixin, PollMessage):
    """Domain deletion poll message.

    Attributes:
        name: Content of the epp/response/msgQ/msg/delData/name element.
        ex_date: Content of the epp/response/msgQ/msg/delData/exDate element.
    """

    tag = QName(NAMESPACE.NIC_DOMAIN, 'delData')

    name: str
    ex_date: date

    @classmethod
    def extract(cls, element: Element) -> 'DomainDeletion':
        """Extract the Message from the element."""
        name = cls._find_text(element, './domain:name')
        ex_date = cls._parse_date(cls._find_text(element, 'domain:exDate'))
        return cls(name=name, ex_date=ex_date)


@dataclass
class TechnicalCheckResult(ParseXMLMixin, PollMessage):
    """Technical check result poll message.

    Attributes:
        id: Content of the epp/response/msgQ/msg/testData/id element.
        names: Content of the epp/response/msgQ/msg/testData/name elements.
        results: Content of the epp/response/msgQ/msg/testData/results element.
    """

    tag = QName(NAMESPACE.NIC_NSSET, 'testData')

    id: str
    names: Sequence[str]
    results: Sequence[TestResult]

    @classmethod
    def extract(cls, element: Element) -> 'TechnicalCheckResult':
        """Extract the Message from the element."""
        id = cls._find_text(element, './nsset:id')
        names = cls._find_all_text(element, './nsset:name')
        results = [TestResult.extract(item) for item in cls._find_all(element, './nsset:result')]
        return cls(id=id, names=names, results=results)


POLL_MESSAGE_TYPES: Mapping[QName, Type['PollMessage']] = {
    LowCredit.tag: LowCredit,
    RequestUsage.tag: RequestUsage,
    ImpendingExpData.tag: ImpendingExpData,
    ExpData.tag: ExpData,
    DnsOutageData.tag: DnsOutageData,
    DelData.tag: DelData,
    ImpendingValExpData.tag: ImpendingValExpData,
    ValExpData.tag: ValExpData,
    DomainTransfer.tag: DomainTransfer,
    ContactTransfer.tag: ContactTransfer,
    KeysetTransfer.tag: KeysetTransfer,
    NssetTransfer.tag: NssetTransfer,
    DomainUpdate.tag: DomainUpdate,
    ContactUpdate.tag: ContactUpdate,
    KeysetUpdate.tag: KeysetUpdate,
    NssetUpdate.tag: NssetUpdate,
    IdleContactDeletion.tag: IdleContactDeletion,
    IdleKeysetDeletion.tag: IdleKeysetDeletion,
    IdleNssetDeletion.tag: IdleNssetDeletion,
    DomainDeletion.tag: DomainDeletion,
    TechnicalCheckResult.tag: TechnicalCheckResult,
}
