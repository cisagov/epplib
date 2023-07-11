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

"""Module providing models for EPP info responses."""

from dataclasses import dataclass, field, InitVar
from datetime import date, datetime
from typing import Any, ClassVar, List, Mapping, Optional, Sequence, Union

from dateutil.parser import parse as parse_datetime
from lxml.etree import Element

from epplib.models import (
    ContactAuthInfo,
    Disclose,
    Dnskey,
    DomainAuthInfo,
    DomainContact,
    ExtractModelMixin,
    Ident,
    Ip,
    Ns,
    PostalInfo,
    Status,
)


@dataclass
class InfoResultData(ExtractModelMixin):
    """Dataclass representing queried item info in the info result.

    Attributes:
        roid: Content of the epp/response/resData/infData/roid element.
        statuses: Content of the epp/response/resData/infData/status element.
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
    """

    _namespace: ClassVar[str]

    roid: str
    statuses: List[Status]
    cl_id: str
    cr_id: Optional[str]
    cr_date: Optional[datetime]
    up_id: Optional[str]
    up_date: Optional[datetime]
    tr_date: Optional[datetime]

    @classmethod
    def extract(cls, element: Element) -> "InfoResultData":
        """Extract params for own init from the element."""
        return cls(**cls._get_params(element))

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "roid": cls._find_text(element, f"./{cls._namespace}:roid"),
            "statuses": [
                Status.extract(item)
                for item in cls._find_all(element, f"./{cls._namespace}:status")
            ],
            "cl_id": cls._find_text(element, f"./{cls._namespace}:clID"),
            "cr_id": cls._find_text(element, f"./{cls._namespace}:crID"),
            "cr_date": cls._optional(
                parse_datetime, cls._find_text(element, f"./{cls._namespace}:crDate")
            ),
            "up_id": cls._find_text(element, f"./{cls._namespace}:upID"),
            "up_date": cls._optional(
                parse_datetime, cls._find_text(element, f"./{cls._namespace}:upDate")
            ),
            "tr_date": cls._optional(
                parse_datetime, cls._find_text(element, f"./{cls._namespace}:trDate")
            ),
        }
        return params


@dataclass
class InfoDomainResultData(InfoResultData):
    """Dataclass representing domain info in the info domain result.

    Attributes:
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
        auth_info: Content of the epp/response/resData/infData/authInfo element.
        name: Content of the epp/response/resData/infData/name element.
        registrant: Content of the epp/response/resData/infData/registrant element.
        admins: Content of the epp/response/resData/infData/admin element.
        nsset: Content of the epp/response/resData/infData/nsset element.
        keyset: Content of the epp/response/resData/infData/keyset element.
        ex_date: Content of the epp/response/resData/infData/exDate element.
        hosts: Content of the epp/response/resData/infData/ns/hostObj element.
        contacts: Content of the epp/response/resData/infData/contact element.
    """

    _namespace = "domain"

    name: str
    registrant: Optional[str]
    admins: List[str]
    nsset: Optional[str]
    keyset: Optional[str]
    ex_date: Optional[date]
    auth_info: Optional[Union[str, DomainAuthInfo]]
    hosts: InitVar[Optional[List[str]]] = None
    contacts: InitVar[Optional[List[str]]] = None

    def __post_init__(self, hosts, contacts) -> None:
        self.hosts = hosts or []
        self.contacts = contacts or []

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "name": cls._find_text(element, f"./{cls._namespace}:name"),
            "registrant": cls._find_text(element, f"./{cls._namespace}:registrant"),
            "admins": cls._find_all_text(element, f"./{cls._namespace}:admin"),
            "nsset": cls._find_text(element, f"./{cls._namespace}:nsset"),
            "keyset": cls._find_text(element, f"./{cls._namespace}:keyset"),
            "ex_date": cls._optional(
                cls._parse_date, cls._find_text(element, f"./{cls._namespace}:exDate")
            ),
            "auth_info": cls._optional(
                DomainAuthInfo.extract,
                cls._find(element, f"./{cls._namespace}:authInfo"),
            ),
        }
        ns = cls._find(element, f"./{InfoDomainResultData._namespace}:ns")
        contacts = cls._find_all(element, f"./{cls._namespace}:contact")
        if ns is not None:
            params["hosts"] = cls._find_all_text(ns, f"./{cls._namespace}:hostObj")
        if contacts:
            params["contacts"] = [DomainContact.extract(item) for item in contacts]
        return {**super()._get_params(element), **params}


@dataclass
class InfoHostResultData(InfoResultData):
    """Dataclass representing host info in the info host result.

    Attributes:
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
        name: Content of the epp/response/resData/infData/name element.
        addrs: Content of the epp/response/resData/infData/addr element.
        statuses: Content of the epp/response/resData/infData/status element.
    """

    _namespace = "host"

    name: str
    addrs: Optional[List[Ip]] = field(default_factory=list)

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "name": cls._find_text(element, f"./{cls._namespace}:name"),
            "addrs": [
                Ip.extract(item)
                for item in cls._find_all(element, f"./{cls._namespace}:addr")
            ],
        }
        return {**super()._get_params(element), **params}


@dataclass
class InfoContactResultData(InfoResultData):
    """Dataclass representing contact info in the info contact result.

    Attributes:
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
        auth_info: Content of the epp/response/resData/infData/authInfo element.
        id: Content of the epp/response/resData/infData/id element.
        postal_info: Content of the epp/response/resData/infData/postalInfo element.
        voice: Content of the epp/response/resData/infData/voice element.
        fax: Content of the epp/response/resData/infData/fax element.
        email: Content of the epp/response/resData/infData/email element.
        disclose: Content of the epp/response/resData/infData/disclose element.
        vat: Content of the epp/response/resData/infData/vat element.
        ident: Content of the epp/response/resData/infData/ident element.
        notify_email: Content of the epp/response/resData/infData/notifyEmail element.
    """

    _namespace = "contact"

    id: str
    postal_info: PostalInfo
    voice: Optional[str]
    fax: Optional[str]
    email: Optional[str]
    disclose: Optional[Disclose]
    vat: Optional[str]
    ident: Optional[Ident]
    notify_email: Optional[str]
    auth_info: Optional[Union[str, ContactAuthInfo]]

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "id": cls._find_text(element, f"./{cls._namespace}:id"),
            "postal_info": PostalInfo.extract(
                cls._find(element, f"./{cls._namespace}:postalInfo")
            ),
            "voice": cls._find_text(element, f"./{cls._namespace}:voice"),
            "fax": cls._find_text(element, f"./{cls._namespace}:fax"),
            "email": cls._find_text(element, f"./{cls._namespace}:email"),
            "disclose": cls._optional(
                Disclose.extract, cls._find(element, f"./{cls._namespace}:disclose")
            ),
            "vat": cls._find_text(element, f"./{cls._namespace}:vat"),
            "ident": cls._optional(
                Ident.extract, cls._find(element, f"./{cls._namespace}:ident")
            ),
            "notify_email": cls._find_text(element, f"./{cls._namespace}:notifyEmail"),
            "auth_info": cls._optional(
                ContactAuthInfo.extract,
                cls._find(element, f"./{cls._namespace}:authInfo"),
            ),
        }
        return {**super()._get_params(element), **params}


@dataclass
class InfoKeysetResultData(InfoResultData):
    """Dataclass representing keyset info in the info keyset result.

    Attributes:
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
        auth_info: Content of the epp/response/resData/infData/authInfo element.
        id: Content of the epp/response/resData/infData/id element.
        dnskeys: Content of the epp/response/resData/infData/dnskey elements.
        techs: Content of the epp/response/resData/infData/tech elements.
    """

    _namespace = "keyset"

    id: str
    dnskeys: Sequence[Dnskey]
    techs: Sequence[str]
    auth_info: Optional[str]

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "id": cls._find_text(element, f"./{cls._namespace}:id"),
            "dnskeys": [
                Dnskey.extract(item)
                for item in cls._find_all(element, f"./{cls._namespace}:dnskey")
            ],
            "techs": cls._find_all_text(element, f"./{cls._namespace}:tech"),
            "auth_info": cls._find_text(element, f"./{cls._namespace}:authInfo"),
        }
        return {**super()._get_params(element), **params}


@dataclass
class InfoNssetResultData(InfoResultData):
    """Dataclass representing nsset info in the info nsset result.

    Attributes:
        cl_id: Content of the epp/response/resData/infData/clID element.
        cr_id: Content of the epp/response/resData/infData/crID element.
        cr_date: Content of the epp/response/resData/infData/crDate element.
        up_id: Content of the epp/response/resData/infData/upID element.
        up_date: Content of the epp/response/resData/infData/upDate element.
        tr_date: Content of the epp/response/resData/infData/trDate element.
        auth_info: Content of the epp/response/resData/infData/authInfo element.
        id: Content of the epp/response/resData/infData/id element.
        nss: Content of the epp/response/resData/infData/ns elements.
        techs: Content of the epp/response/resData/infData/tech elements.
        reportlevel: Content of the epp/response/resData/infData/reportlevel elements.
    """

    _namespace = "nsset"

    id: str
    nss: Sequence[Ns]
    techs: Sequence[str]
    reportlevel: int
    auth_info: Optional[str]

    @classmethod
    def _get_params(cls, element: Element) -> Mapping[str, Any]:
        params: Mapping[str, Any] = {
            "id": cls._find_text(element, f"./{cls._namespace}:id"),
            "nss": [
                Ns.extract(item)
                for item in cls._find_all(element, f"./{cls._namespace}:ns")
            ],
            "techs": cls._find_all_text(element, f"./{cls._namespace}:tech"),
            "reportlevel": int(
                cls._find_text(element, f"./{cls._namespace}:reportlevel")
            ),
            "auth_info": cls._find_text(element, f"./{cls._namespace}:authInfo"),
        }
        return {**super()._get_params(element), **params}
