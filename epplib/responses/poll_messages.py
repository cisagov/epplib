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

"""Module providing classes for EPP poll messages."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar, Mapping, Type, cast

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element, QName

from epplib.constants import NAMESPACE
from epplib.utils import ParseXMLMixin


class PollMessage(ABC):
    """Base class for poll messages."""

    tag: ClassVar[QName]

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'PollMessage':
        """Extract the Message from the element."""


@dataclass
class LowCredit(ParseXMLMixin, PollMessage):
    """Low credit poll message."""

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
    """Request usage poll message."""

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
    """Domain expiration poll message."""

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
    """Domain validation poll message."""

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
    """Object transfer poll message."""

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
    """Domain transfer poll message."""

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
    """Contact transfer poll message."""

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
    """Keyset transfer poll message."""

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
    """Nsset transfer poll message."""

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
class IdleObjectDeletion(ParseXMLMixin, PollMessage):
    """Idle object deletion poll message."""

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
    IdleContactDeletion.tag: IdleContactDeletion,
    IdleKeysetDeletion.tag: IdleKeysetDeletion,
    IdleNssetDeletion.tag: IdleNssetDeletion,
}
