#
# Copyright (C) 2021-2023  CZ.NIC, z. s. p. o.
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
#
"""Common models used accross epplib."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import ClassVar, List, Mapping, Optional, Sequence, Set, Union, cast

from lxml.etree import Element, QName, SubElement

from epplib.constants import NAMESPACE
from epplib.utils import ParseXMLMixin


@unique
class DiscloseField(str, Enum):
    """Allowed values of subelements of disclose element."""

    # Order matters! Elements are ordered by their position within disclose flag.
    ADDR = "addr"
    VOICE = "voice"
    FAX = "fax"
    EMAIL = "email"
    VAT = "vat"
    IDENT = "ident"
    NOTIFY_EMAIL = "notifyEmail"


@unique
class IdentType(str, Enum):
    """Allowed values of the type attribure of ident."""

    OP = "op"
    PASSPORT = "passport"
    MPSV = "mpsv"
    ICO = "ico"
    BIRTHDAY = "birthday"


@unique
class Unit(str, Enum):
    """Unit for registration period."""

    MONTH = "m"
    YEAR = "y"


class ExtractModelMixin(ParseXMLMixin, ABC):
    """Mixin for model which are deserializable from XML."""

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> "ExtractModelMixin":
        """Extract the model from the element."""


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
class Addr(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP addr element.

    Attributes:
        street: Content of the addr/street element.
        city: Content of the addr/city element.
        pc: Content of the addr/pc element.
        cc: Content of the addr/cc element.
        sp: Content of the addr/sp element.
    """

    _alias: ClassVar[str]

    street: Sequence[str]
    city: Optional[str]
    pc: Optional[str]
    cc: Optional[str]
    sp: Optional[str] = None

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        addr = Element(QName(self.namespace, "addr"))
        for line in self.street:
            SubElement(addr, QName(self.namespace, "street")).text = line
        SubElement(addr, QName(self.namespace, "city")).text = self.city
        if self.sp:
            SubElement(addr, QName(self.namespace, "sp")).text = self.sp
        SubElement(addr, QName(self.namespace, "pc")).text = self.pc
        SubElement(addr, QName(self.namespace, "cc")).text = self.cc
        return addr

    @classmethod
    def extract(cls, element: Element) -> "Addr":
        """Extract the model from the element."""
        return cls(
            street=cls._find_all_text(element, f"./{cls._alias}:street"),
            city=cls._find_text(element, f"./{cls._alias}:city"),
            pc=cls._find_text(element, f"./{cls._alias}:pc"),
            cc=cls._find_text(element, f"./{cls._alias}:cc"),
            sp=cls._find_text(element, f"./{cls._alias}:sp"),
        )


@dataclass
class AuthInfo(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP authInfo element.

    Attributes:
        pw: Content of the authInfo/pw element.
    """

    pw: Optional[str]

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        auth_info = Element(QName(self.namespace, "authInfo"))
        SubElement(auth_info, QName(self.namespace, "pw")).text = self.pw
        return auth_info

    @classmethod
    def extract(cls, element: Element) -> Union[str, "AuthInfo"]:
        """Extract the model from the element."""
        pw = cls._find_text(element, "./{*}pw")
        if pw is None:
            return element.text
        return cls(pw=pw)


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

    _alias = "contact"
    namespace = NAMESPACE.NIC_CONTACT

    @classmethod
    def extract(cls, element: Element) -> "ContactAddr":
        """Extract the model from the element."""
        return cast("ContactAddr", super().extract(element))


@dataclass
class ContactAuthInfo(AuthInfo):
    """Dataclass to represent EPP contact:authInfo element.

    Attributes:
        pw: Content of the authInfo/pw element.
    """

    namespace = NAMESPACE.NIC_CONTACT

    @classmethod
    def extract(cls, element: Element) -> "ContactAuthInfo":
        """Extract the model from the element."""
        return cast("ContactAuthInfo", super().extract(element))


@dataclass
class Disclose(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP disclose element.

    Attributes:
        flag: disclose flag attribute.
        fields: Values to be displayed as subelements of the disclose element.
    """

    namespace = NAMESPACE.NIC_CONTACT

    flag: Optional[bool]
    fields: Set[DiscloseField]
    types: Optional[Mapping[DiscloseField, str]] = None

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        flag = "1" if self.flag else "0"
        disclose = Element(QName(self.namespace, "disclose"), flag=flag)
        for item in sorted(self.fields, key=tuple(DiscloseField).index):
            if self.types and item in self.types:
                type = self.types[item]
                SubElement(disclose, QName(self.namespace, item.value), type=type)
            else:
                SubElement(disclose, QName(self.namespace, item.value))
        return disclose

    @classmethod
    def extract(cls, element: Element) -> "Disclose":
        """Extract the model from the element."""
        return cls(
            flag=cls._str_to_bool(cls._find_attrib(element, ".", "flag")),
            fields=set(
                DiscloseField(item) for item in cls._find_children(element, "./")
            ),
        )


@dataclass
class DomainAuthInfo(AuthInfo):
    """Dataclass to represent EPP domain:authInfo element.

    Attributes:
        pw: Content of the authInfo/pw element.
    """

    namespace = NAMESPACE.NIC_DOMAIN

    @classmethod
    def extract(cls, element: Element) -> "DomainAuthInfo":
        """Extract the model from the element."""
        return cast("DomainAuthInfo", super().extract(element))


@dataclass
class DomainContact(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP domain:contact element.

    Attributes:
        contact: Content of the contact element.
        type: Content of the type attribute of the contact element.
    """

    namespace = NAMESPACE.NIC_DOMAIN

    contact: str
    type: str

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        domain_contact = Element(QName(self.namespace, "contact"))
        domain_contact.text = self.contact
        domain_contact.set("type", self.type)
        return domain_contact

    @classmethod
    def extract(cls, element: Element) -> "DomainContact":
        """Extract the model from the element."""
        return cls(contact=element.text, type=element.get("type"))


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

    _alias = "extra-addr"
    _NAMESPACES: ClassVar[Mapping[str, str]] = {
        **ParseXMLMixin._NAMESPACES,
        _alias: NAMESPACE.NIC_EXTRA_ADDR,
    }
    namespace = NAMESPACE.NIC_EXTRA_ADDR

    @classmethod
    def extract(cls, element: Element) -> "ExtraAddr":
        """Extract the model from the element."""
        return cast("ExtraAddr", super().extract(element))


@dataclass
class Dnskey(PayloadModelMixin, ExtractModelMixin):
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
        dnskey = Element(QName(self.namespace, "dnskey"))
        SubElement(dnskey, QName(self.namespace, "flags")).text = str(self.flags)
        SubElement(dnskey, QName(self.namespace, "protocol")).text = str(self.protocol)
        SubElement(dnskey, QName(self.namespace, "alg")).text = str(self.alg)
        SubElement(dnskey, QName(self.namespace, "pubKey")).text = self.pub_key
        return dnskey

    @classmethod
    def extract(cls, element: Element) -> "Dnskey":
        """Extract the model from the element."""
        flags = int(cls._find_text(element, "./keyset:flags"))
        protocol = int(cls._find_text(element, "./keyset:protocol"))
        alg = int(cls._find_text(element, "./keyset:alg"))
        pub_key = cls._find_text(element, "./keyset:pubKey")

        return cls(flags=flags, protocol=protocol, alg=alg, pub_key=pub_key)


@dataclass
class HostObjSet(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP domain:ns element.

    Attributes:
        hosts: Content of the ns/hostObj tag.
    """

    namespace = NAMESPACE.NIC_DOMAIN

    hosts: List[str] = field(default_factory=list)

    def get_payload(self) -> Element:
        """Get Element representing the the model."""
        ns = Element(QName(self.namespace, "ns"))
        for host in self.hosts:
            SubElement(ns, QName(self.namespace, "hostObj")).text = host
        return ns

    @classmethod
    def extract(cls, element: Element) -> "Dnskey":
        """Extract the model from the element."""
        ns = cls._find(element, f"./{cls.namespace}:ns")
        if ns is not None:
            return cls(hosts=cls._find_all_text(ns, f"./{cls._namespace}:hostObj"))
        else:
            return []


@dataclass
class Ident(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP ident element.

    Attributes:
        type: type attribute of the ident tag.
        value: Content of the ident tag.
    """

    namespace = NAMESPACE.NIC_CONTACT

    type: IdentType
    value: str

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        ident = Element(QName(self.namespace, "ident"), type=self.type)
        ident.text = self.value
        return ident

    @classmethod
    def extract(cls, element: Element) -> "Ident":
        """Extract the model from the element."""
        type = IdentType(cls._find_attrib(element, ".", "type"))
        value = cls._find_text(element, ".")
        return cls(type=type, value=value)


@dataclass
class Ip(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP addr element.

    Attributes:
        addr: Content of the addr element.
        ip: Content of the ip attribute of the addr element.
    """

    namespace = NAMESPACE.NIC_HOST

    addr: str
    ip: Optional[str] = None

    def get_payload(self) -> Element:
        """Get Element representing the the model."""
        addr = Element(QName(self.namespace, "addr"))
        addr.text = self.addr
        if self.ip is not None:
            addr.set("ip", self.ip)
        return addr

    @classmethod
    def extract(cls, element: Element) -> "Ip":
        """Extract the model from the element."""
        addr = cls._find_text(element, ".")
        ip = cls._find_attrib(element, ".", "ip")
        return cls(addr=addr, ip=ip)


@dataclass
class Ns(PayloadModelMixin, ExtractModelMixin):
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
        ns = Element(QName(self.namespace, "ns"))
        SubElement(ns, QName(self.namespace, "name")).text = self.name
        for addr in self.addrs:
            SubElement(ns, QName(self.namespace, "addr")).text = addr
        return ns

    @classmethod
    def extract(cls, element: Element) -> "Ns":
        """Extract the model from the element."""
        name = cls._find_text(element, "./nsset:name")
        addrs = cls._find_all_text(element, "./nsset:addr")
        return cls(name=name, addrs=addrs)


@dataclass
class Period(PayloadModelMixin):
    """Dataclass to represent EPP period element.

    Attributes:
        length: Content of the period element.
        unit: Content of the unit attribute of the period element.
    """

    namespace = NAMESPACE.NIC_DOMAIN

    length: int
    unit: Unit

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        period = Element(QName(self.namespace, "period"))
        period.attrib["unit"] = self.unit.value
        period.text = str(self.length)

        return period


@dataclass
class PostalInfo(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP postalInfo element.

    Attributes:
        name: Content of the postalInfo/name element.
        addr: Content of the postalInfo/addr element.
        org: Content of the postalInfo/org element.
        type: Content of the postalInfo type attribute.
    """

    namespace = NAMESPACE.NIC_CONTACT

    name: Optional[str] = None
    addr: Optional[ContactAddr] = None
    org: Optional[str] = None
    type: Optional[str] = None

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        postal_info = Element(QName(self.namespace, "postalInfo"))

        if self.name:
            SubElement(postal_info, QName(self.namespace, "name")).text = self.name
        if self.type is not None:
            postal_info.set("type", self.type)
        if self.org is not None:
            SubElement(postal_info, QName(self.namespace, "org")).text = self.org
        if self.addr:
            postal_info.append(self.addr.get_payload())

        return postal_info

    @classmethod
    def extract(cls, element: Element) -> "PostalInfo":
        """Extract the model from the element."""
        name = cls._find_text(element, "./contact:name")
        org = cls._find_text(element, "./contact:org")
        addr = cls._optional(ContactAddr.extract, cls._find(element, "./contact:addr"))
        return cls(name=name, addr=addr, org=org)


@dataclass
class Statement(ExtractModelMixin):
    """A dataclass to represent the EPP statement.

    Attributes:
        purpose: Content of the epp/greeting/statement/purpose element.
        recipient: Content of the epp/greeting/statement/recipient element.
        retention: Content of the epp/greeting/statement/retention element.
    """

    purpose: List[str]
    recipient: List[str]
    retention: Optional[str]

    @classmethod
    def extract(cls, element: Element) -> "Statement":
        """Extract the model from the element."""
        return cls(
            purpose=cls._find_children(element, "./epp:purpose"),
            recipient=cls._find_children(element, "./epp:recipient"),
            retention=cls._find_child(element, "./epp:retention"),
        )


@dataclass
class Status(PayloadModelMixin, ExtractModelMixin):
    """Represents a status of the queried object in the InfoResult."""

    namespace = NAMESPACE.NIC_DOMAIN

    state: str
    description: str
    lang: Optional[str] = None

    def __post_init__(self) -> None:
        if self.lang is None:
            self.lang = "en"

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        status = Element(QName(self.namespace, "status"))
        status.set("s", self.state)
        return status

    @classmethod
    def extract(cls, element: Element) -> "Status":
        """Extract the model from the element."""
        return cls(element.get("s"), element.text, element.get("lang"))


@dataclass
class HostStatus(PayloadModelMixin, ExtractModelMixin):
    """Dataclass to represent EPP host:status element.

    Attributes:
        s: Content of the s attribute of the status element.
    """

    namespace = NAMESPACE.NIC_HOST

    s: str

    def get_payload(self) -> Element:
        """Get Element representing the model."""
        status = Element(QName(self.namespace, "status"))
        status.set("s", self.s)
        return status

    @classmethod
    def extract(cls, element: Element) -> "Status":
        """Extract the model from the element."""
        return cls(s=element.get("s"))


@dataclass
class TestResult(ExtractModelMixin):
    """Represent result element in Technical check result poll message."""

    testname: str
    status: Optional[bool]
    note: Optional[str]

    @classmethod
    def extract(cls, element: Element) -> "TestResult":
        """Extract the model from the element."""
        testname = cls._find_text(element, "./nsset:testname")
        status = cls._str_to_bool(cls._find_text(element, "./nsset:status"))
        note = cls._find_text(element, "./nsset:note")
        return cls(testname=testname, status=status, note=note)
