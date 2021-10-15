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

"""Module providing EPP commands."""
from dataclasses import dataclass
from typing import Optional, Sequence

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION, Unit
from epplib.models import Disclose, Ident, Ns, PostalInfo
from epplib.responses import CreateContactResult, CreateDomainResult, CreateNssetResult


@dataclass
class CreateDomain(Command):
    """EPP Create Domain command.

    Attributes:
        name: Domain name to register
        registrant: Registrant ID
        period: Period of the registration validity
        unit: Unit of period - one of 'y', 'm' for years, months respectively
        nsset: nsset ID
        keyset: keyset ID
        admin: administrator contact ID
        auth_info: authInfo for domain transfers
    """

    response_class = CreateDomainResult

    name: str
    registrant: str
    period: Optional[int] = None
    unit: Unit = Unit.YEAR
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    admin: Optional[str] = None
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CreateDomain.

        Returns:
            Element with a domain to create.
        """
        create = Element(QName(NAMESPACE.EPP, 'create'))

        domain_create = SubElement(create, QName(NAMESPACE.NIC_DOMAIN, 'create'))
        domain_create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)

        SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name
        if self.period is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'period'), unit=self.unit).text = str(self.period)
        if self.nsset is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'nsset')).text = self.nsset
        if self.keyset is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'keyset')).text = self.keyset
        SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'registrant')).text = self.registrant
        if self.admin is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = self.admin
        if self.auth_info is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'authInfo')).text = self.auth_info

        return create


@dataclass
class CreateContact(Command):
    """EPP Create Contact command.

    Attributes:
        id: Content of command/create/create/id tag.
        postal_info: Content of command/create/create/postalInfo tag.
        email: Content of command/create/create/email tag.
        voice: Content of command/create/create/voice tag.
        fax: Content of command/create/create/fax tag.
        auth_info: Content of command/create/create/authInfo tag.
        disclose: Content of command/create/create/disclose tag.
        vat: Content of command/create/create/vat tag.
        ident: Content of command/create/create/ident tag.
        notify_email: Content of command/create/create/notifyEmail tag.
    """

    response_class = CreateContactResult

    id: str
    postal_info: PostalInfo
    email: str
    voice: Optional[str] = None
    fax: Optional[str] = None
    auth_info: Optional[str] = None
    disclose: Optional[Disclose] = None
    vat: Optional[str] = None
    ident: Optional[Ident] = None
    notify_email: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CreateContact.

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
        if self.auth_info:
            SubElement(contact_create, QName(NAMESPACE.NIC_CONTACT, 'authInfo')).text = self.auth_info
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
class CreateNsset(Command):
    """EPP Create Nsset command.

    Attributes:
        id: Content of command/create/create/id tag.
        nss: Content of command/create/create/nss tag.
        tech: Content of command/create/create/tech tag.
        auth_info: Content of command/create/create/authInfo tag.
        report_level: Content of command/create/create/reportlevel tag.
    """

    response_class = CreateNssetResult

    id: str
    nss: Sequence[Ns]
    tech: Sequence[str]
    auth_info: Optional[str] = None
    report_level: Optional[int] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CreateContact.

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
        if self.report_level is not None:
            SubElement(nsset_create, QName(NAMESPACE.NIC_NSSET, 'reportlevel')).text = str(self.report_level)
        return create
