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

"""Module providing EPP create commands."""
from dataclasses import dataclass, field
from typing import Optional, Sequence, Union

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import AuthInfo, Disclose, Dnskey, Ident, Ip, Ns, Period, Unit
from epplib.models.create import CreatePostalInfo
from epplib.responses import (CreateContactResult, CreateDomainResult, CreateHostResult, CreateKeysetResult,
                              CreateNssetResult)


@dataclass
class CreateDomain(Command):
    """EPP Create Domain command.

    Attributes:
        name: Content of the epp/command/create/create/name element.
        registrant: Content of the epp/command/create/create/registrant element.
        period: Content of the epp/command/create/create/period element.
        nsset: Content of the epp/command/create/create/nsset element.
        keyset: Content of the epp/command/create/create/keyset element.
        admins: Content of the epp/command/create/create/admin elements.
        auth_info: Content of the epp/command/create/create/authInfo element.
                   This is a string with FRED XML schema but AuthInfo object with IETF.
    """

    response_class = CreateDomainResult

    name: str
    registrant: str
    period: Optional[Period] = None
    unit: Unit = Unit.YEAR
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    admins: Sequence[str] = field(default_factory=list)
    auth_info: Optional[Union[str, AuthInfo]] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for CreateDomain.

        Returns:
            Element with a domain to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))

        domain_create = SubElement(create, QName(NAMESPACE.NIC_DOMAIN, 'create'))
        domain_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)

        SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name
        if self.period is not None:
            domain_create.append(self.period.get_payload())
        if self.nsset is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'nsset')).text = self.nsset
        if self.keyset is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'keyset')).text = self.keyset
        SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'registrant')).text = self.registrant
        for item in self.admins:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = item
        if self.auth_info is not None:
            if isinstance(self.auth_info, str):
                SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'authInfo')).text = self.auth_info
            elif isinstance(self.auth_info, AuthInfo):
                domain_create.append(self.auth_info.get_payload())

        return create

    def add_secDNS_extension(self, maxSigLife)-> None:
        self.add_extension()

@dataclass
class CreateContact(Command):
    """EPP Create Contact command.

    Attributes:
        id: Content of command/create/create/id element.
        postal_info: Content of command/create/create/postalInfo element.
        email: Content of command/create/create/email element.
        voice: Content of command/create/create/voice element.
        fax: Content of command/create/create/fax element.
        auth_info: Content of command/create/create/authInfo element.
                   This is a string with FRED XML schema but AuthInfo object with IETF.
        disclose: Content of command/create/create/disclose element.
        vat: Content of command/create/create/vat element.
        ident: Content of command/create/create/ident element.
        notify_email: Content of command/create/create/notifyEmail element.
    """

    response_class = CreateContactResult

    id: str
    postal_info: CreatePostalInfo
    email: str
    voice: Optional[str] = None
    fax: Optional[str] = None
    auth_info: Optional[Union[str, AuthInfo]] = None
    disclose: Optional[Disclose] = None
    vat: Optional[str] = None
    ident: Optional[Ident] = None
    notify_email: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for CreateContact.

        Returns:
            Element with a contact to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))

        contact_create = SubElement(create, QName(NAMESPACE.NIC_CONTACT, 'create'))
        contact_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_CONTACT)

        SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'id')).text = self.id
        contact_create.append(self.postal_info.get_payload())
        if self.voice:
            SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'voice')).text = self.voice
        if self.fax:
            SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'fax')).text = self.fax
        SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'email')).text = self.email
        if self.auth_info is not None:
            if isinstance(self.auth_info, str):
                SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'authInfo')).text = self.auth_info
            elif isinstance(self.auth_info, AuthInfo):
                contact_create.append(self.auth_info.get_payload())
        if self.disclose:
            contact_create.append(self.disclose.get_payload())
        if self.vat:
            SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'vat')).text = self.vat
        if self.ident:
            contact_create.append(self.ident.get_payload())
        if self.notify_email:
            SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'notifyEmail')).text = self.notify_email

        return create


@dataclass
class CreateHost(Command):
    """EPP Create Host command.

    Attributes:
        name: Content of command/create/create/name element.
        addrs: Content of command/create/create/addr element.
    """

    response_class = CreateHostResult

    name: str
    addrs: Optional[Sequence[Ip]] = field(default_factory=list)

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for CreateHost.

        Returns:
            Element with a host to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))

        host_create = SubElement(create, QName(NAMESPACE.NIC_HOST, 'create'))
        host_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_HOST)

        SubElement(host_create, QName(NAMESPACE.NIC_HOST, 'name')).text = self.name
        for addr in self.addrs:
            host_create.append(addr.get_payload())

        return create


@dataclass
class CreateNsset(Command):
    """EPP Create Nsset command.

    Attributes:
        id: Content of command/create/create/id element.
        nss: Content of command/create/create/nss element.
        tech: Content of command/create/create/tech element.
        auth_info: Content of command/create/create/authInfo element.
        reportlevel: Content of command/create/create/reportlevel element.
    """

    response_class = CreateNssetResult

    id: str
    nss: Sequence[Ns]
    tech: Sequence[str]
    auth_info: Optional[str] = None
    reportlevel: Optional[int] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for CreateContact.

        Returns:
            Element with a contact to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))
        nsset_create = SubElement(create, QName(NAMESPACE.NIC_NSSET, 'create'))
        nsset_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_NSSET)
        SubElement(nsset_create, QName(NAMESPACE.NIC_NSSET, 'id')).text = self.id
        for ns in self.nss:
            nsset_create.append(ns.get_payload())
        for item in self.tech:
            SubElement(nsset_create, QName(NAMESPACE.NIC_NSSET, 'tech')).text = item
        if self.auth_info is not None:
            SubElement(nsset_create, QName(NAMESPACE.NIC_NSSET, 'authInfo')).text = self.auth_info
        if self.reportlevel is not None:
            SubElement(nsset_create, QName(NAMESPACE.NIC_NSSET, 'reportlevel')).text = str(self.reportlevel)
        return create


@dataclass
class CreateKeyset(Command):
    """EPP Create Keyset command.

    Attributes:
        id: Content of command/create/create/id element.
        dnskeys: Content of command/create/create/dnskey elements.
        tech: Content of command/create/create/tech element.
        auth_info: Content of command/create/create/authInfo element.
    """

    response_class = CreateKeysetResult

    id: str
    dnskeys: Sequence[Dnskey]
    tech: Sequence[str]
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for CreateContact.

        Returns:
            Element with a contact to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))
        keyset_create = SubElement(create, QName(NAMESPACE.NIC_KEYSET, 'create'))
        keyset_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_KEYSET)
        SubElement(keyset_create, QName(NAMESPACE.NIC_KEYSET, 'id')).text = self.id
        for dns_key in self.dnskeys:
            keyset_create.append(dns_key.get_payload())
        for item in self.tech:
            SubElement(keyset_create, QName(NAMESPACE.NIC_KEYSET, 'tech')).text = item
        if self.auth_info is not None:
            SubElement(keyset_create, QName(NAMESPACE.NIC_KEYSET, 'authInfo')).text = self.auth_info
        return create
