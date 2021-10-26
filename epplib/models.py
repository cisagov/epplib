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

"""Module providing base classes to EPP command responses."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import ClassVar, List, Optional, Sequence, Set

from lxml.etree import Element, QName, SubElement

from epplib.constants import NAMESPACE


@unique
class DiscloseFields(str, Enum):
    """Allowed values of subelements of disclose element."""

    VOICE = 'voice'
    FAX = 'fax'
    EMAIL = 'email'
    VAT = 'vat'
    IDENT = 'ident'
    NOTIFY_EMAIL = 'notifyEmail'


@unique
class IdentType(str, Enum):
    """Allowed values of the type attribure of ident."""

    OP = 'op'
    PASSPORT = 'passport'
    MPSV = 'mpsv'
    ICO = 'ico'
    BIRTHDAY = 'birthday'


class PayloadModelMixin(ABC):
    """Mixin for model which are serializable to XML.

    Attributes:
        namespace: XML namespace of the model.
    """

    namespace: ClassVar[str]

    @abstractmethod
    def get_payload(self) -> Element:
        """Get Element representing the model."""


@dataclass
class Addr(PayloadModelMixin):
    """Dataclass to represent EPP addr element.

    Attributes:
        street: Content of the addr/street element.
        city: Content of the addr/city element.
        pc: Content of the addr/pc element.
        cc: Content of the addr/cc element.
        sp: Content of the addr/sp element.
    """

    street: Sequence[str]
    city: str
    pc: str
    cc: str
    sp: Optional[str] = None

    def get_payload(self) -> Element:
        """Get Element representing the model.

        Args:
            namespace: Namespace to prefix the subelement tag names.
        """
        addr = Element(QName(self.namespace, 'addr'))
        for line in self.street:
            SubElement(addr, QName(self.namespace, 'street')).text = line
        SubElement(addr, QName(self.namespace, 'city')).text = self.city
        if self.sp:
            SubElement(addr, QName(self.namespace, 'sp')).text = self.sp
        SubElement(addr, QName(self.namespace, 'pc')).text = self.pc
        SubElement(addr, QName(self.namespace, 'cc')).text = self.cc
        return addr


@dataclass
class ContactAddr(Addr):
    """Dataclass to represent EPP contact:addr element.

    Attributes:
        street: Content of the addr/street element.
        city: Content of the addr/city element.
        pc: Content of the addr/pc element.
        cc: Content of the addr/cc element.
        sp: Content of the addr/sp element.
    """

    namespace = NAMESPACE.NIC_CONTACT


@dataclass
class Disclose(PayloadModelMixin):
    """Dataclass to represent EPP disclose element.

    Attributes:
        flag: disclose flag attribute.
        fields: Values to be displayed as subelements of the disclose element.
    """

    namespace = NAMESPACE.NIC_CONTACT

    flag: bool
    fields: Set[DiscloseFields]

    def get_payload(self) -> Element:
        """Get Element representing the model.

        Args:
            namespace: Namespace to prefix the subelement tag names.
        """
        flag = '1' if self.flag else '0'
        disclose = Element(QName(self.namespace, 'disclose'), flag=flag)
        for item in sorted(self.fields):
            SubElement(disclose, QName(self.namespace, item.value))
        return disclose


@dataclass
class ExtraAddr(Addr):
    """Dataclass to represent EPP contact:addr element.

    Attributes:
        street: Content of the addr/street element.
        city: Content of the addr/city element.
        pc: Content of the addr/pc element.
        cc: Content of the addr/cc element.
        sp: Content of the addr/sp element.
    """

    namespace = NAMESPACE.NIC_EXTRA_ADDR


@dataclass
class Dnskey(PayloadModelMixin):
    """Dataclass to represent EPP dnskey element.

    Attributes:
        flags: Content of the flags element.
        protocol: Content of the protocol element.
        alg: Content of the alg element.
        pubKey: Content of the pubKey element.
    """

    namespace = NAMESPACE.NIC_KEYSET

    flags: int
    protocol: int
    alg: int
    pub_key: str

    def get_payload(self) -> Element:
        """Get Element representing the the model."""
        dnskey = Element(QName(self.namespace, 'dnskey'))
        SubElement(dnskey, QName(self.namespace, 'flags')).text = str(self.flags)
        SubElement(dnskey, QName(self.namespace, 'protocol')).text = str(self.protocol)
        SubElement(dnskey, QName(self.namespace, 'alg')).text = str(self.alg)
        SubElement(dnskey, QName(self.namespace, 'pubKey')).text = self.pub_key
        return dnskey


@dataclass
class Ident(PayloadModelMixin):
    """Dataclass to represent EPP ident element.

    Attributes:
        type: type attribute of the ident tag.
        value: Content of the ident tag.
    """

    namespace = NAMESPACE.NIC_CONTACT

    type: IdentType
    value: str

    def get_payload(self) -> Element:
        """Get Element representing the model.

        Args:
            namespace: Namespace to prefix the subelement tag names.
        """
        ident = Element(QName(self.namespace, 'ident'), type=self.type)
        ident.text = self.value
        return ident


@dataclass
class Ns(PayloadModelMixin):
    """Dataclass to represent EPP ns element.

    Attributes:
        name: Content of the ns/name element.
        addrs: Content of the ns/addr elements.
    """

    namespace = NAMESPACE.NIC_NSSET

    name: str
    addrs: Sequence[str] = field(default_factory=list)

    def get_payload(self) -> Element:
        """Get Element representing the the model."""
        ns = Element(QName(self.namespace, 'ns'))
        SubElement(ns, QName(self.namespace, 'name')).text = self.name
        for addr in self.addrs:
            SubElement(ns, QName(self.namespace, 'addr')).text = addr
        return ns


@dataclass
class PostalInfo(PayloadModelMixin):
    """Dataclass to represent EPP postalInfo element.

    Attributes:
        name: Content of the postalInfo/name element.
        addr: Content of the postalInfo/addr element.
        org: Content of the postalInfo/org element.
    """

    namespace = NAMESPACE.NIC_CONTACT

    name: str
    addr: ContactAddr
    org: Optional[str] = None

    def get_payload(self) -> Element:
        """Get Element representing the model.

        Args:
            namespace: Namespace to prefix the subelement tag names.
        """
        postal_info = Element(QName(self.namespace, 'postalInfo'))
        SubElement(postal_info, QName(self.namespace, 'name')).text = self.name

        if self.org:
            SubElement(postal_info, QName(self.namespace, 'org')).text = self.org
        postal_info.append(self.addr.get_payload())

        return postal_info


@dataclass
class Statement:
    """A dataclass to represent the EPP statement.

    Attributes:
        purpose: Content of the epp/greeting/statement/purpose element.
        recipient: Content of the epp/greeting/statement/recipient element.
        retention: Content of the epp/greeting/statement/retention element.
    """

    purpose: List[str]
    recipient: List[str]
    retention: Optional[str]


@dataclass
class Status:
    """Represents a status of the queried object in the InfoResult."""

    state: str
    description: str
    lang: Optional[str] = None

    def __post_init__(self):
        if self.lang is None:
            self.lang = 'en'
