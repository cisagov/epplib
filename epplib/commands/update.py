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

"""Module providing EPP update commands."""
from dataclasses import dataclass, field
from typing import Optional, Sequence, Union

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import (
    AuthInfo,
    Disclose,
    Dnskey,
    DomainContact,
    HostObjSet,
    HostStatus,
    Ident,
    Ip,
    Ns,
    PostalInfo,
    Status,
)
from epplib.responses import Result


@dataclass
class UpdateDomain(Command):
    """EPP update domain command.

    Attributes:
        name: Content of epp/command/update/update/name
        add: Content of epp/command/update/update/add/admin
        rem: Content of epp/command/update/update/rem/admin
        nsset: Content of epp/command/update/update/chg/nsset
        keyset: Content of epp/command/update/update/chg/keyset
        registrant: Content of epp/command/update/update/chg/registrant
        auth_info: Content of epp/command/update/update/chg/authInfo
                   This is a string with FRED XML schema but AuthInfo object with IETF.
    """

    response_class = Result

    name: str
    add: Sequence[Union[str, Status, DomainContact, HostObjSet]] = field(
        default_factory=list
    )
    rem: Sequence[Union[str, Status, DomainContact, HostObjSet]] = field(
        default_factory=list
    )
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    registrant: Optional[str] = None
    auth_info: Optional[Union[str, AuthInfo]] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for UpdateDomain.

        Returns:
            Element with a domain to update.
        """
        update = Element(QName(NAMESPACE.EPP, "update"))

        domain_update = SubElement(update, QName(NAMESPACE.NIC_DOMAIN, "update"))
        domain_update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_DOMAIN
        )

        SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, "name")).text = self.name

        if self.add:
            add = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, "add"))
            for item in self.add:
                if isinstance(item, str):
                    SubElement(add, QName(NAMESPACE.NIC_DOMAIN, "admin")).text = item
                elif isinstance(item, (Status, DomainContact, HostObjSet)):
                    add.append(item.get_payload())

        if self.rem:
            rem = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, "rem"))
            for item in self.rem:
                if isinstance(item, str):
                    SubElement(rem, QName(NAMESPACE.NIC_DOMAIN, "admin")).text = item
                elif isinstance(item, (Status, DomainContact, HostObjSet)):
                    rem.append(item.get_payload())

        if (
            self.nsset is not None
            or self.keyset is not None
            or self.registrant is not None
            or self.auth_info is not None
        ):
            chg = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, "chg"))
            if self.nsset is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, "nsset")).text = self.nsset
            if self.keyset is not None:
                SubElement(
                    chg, QName(NAMESPACE.NIC_DOMAIN, "keyset")
                ).text = self.keyset
            if self.registrant is not None:
                SubElement(
                    chg, QName(NAMESPACE.NIC_DOMAIN, "registrant")
                ).text = self.registrant
            if self.auth_info is not None:
                if isinstance(self.auth_info, str):
                    SubElement(
                        chg, QName(NAMESPACE.NIC_DOMAIN, "authInfo")
                    ).text = self.auth_info
                elif isinstance(self.auth_info, AuthInfo):
                    chg.append(self.auth_info.get_payload())

        return update


@dataclass
class UpdateContact(Command):
    """EPP update contact command.

    Attributes:
        id: Content of epp/command/update/update/id element.
        postal_info: Content of epp/command/update/update/chg/postalInfo element.
        voice: Content of epp/command/update/update/chg/voice element.
        fax: Content of epp/command/update/update/chg/fax element.
        email: Content of epp/command/update/update/chg/email element.
        auth_info: Content of epp/command/update/update/chg/authInfo element.
                   This is a string with FRED XML schema but AuthInfo object with IETF.
        disclose: Content of epp/command/update/update/chg/disclose element.
        vat: Content of epp/command/update/update/chg/vat element.
        ident: Content of epp/command/update/update/chg/ident element.
        notify_email: Content of epp/command/update/update/chg/notifyEmail element.
    """

    response_class = Result

    id: str
    postal_info: Optional[PostalInfo] = None
    voice: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    auth_info: Optional[Union[str, AuthInfo]] = None
    disclose: Optional[Disclose] = None
    vat: Optional[str] = None
    ident: Optional[Ident] = None
    notify_email: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for UpdateContact.

        Returns:
            Element with a contact to update.
        """
        update = Element(QName(NAMESPACE.EPP, "update"))

        contact_update = SubElement(update, QName(NAMESPACE.NIC_CONTACT, "update"))
        contact_update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_CONTACT
        )

        SubElement(contact_update, QName(NAMESPACE.NIC_CONTACT, "id")).text = self.id

        change = self._get_change()
        if len(change):
            contact_update.append(change)

        return update

    def _get_change(self) -> Element:
        """Create chg element and its subelements.

        Returns:
            Element with the chg element.
        """
        change = Element(QName(NAMESPACE.NIC_CONTACT, "chg"))

        if self.postal_info is not None:
            change.append(self.postal_info.get_payload())
        if self.voice is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, "voice")).text = self.voice
        if self.fax is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, "fax")).text = self.fax
        if self.email is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, "email")).text = self.email
        if self.auth_info is not None:
            if isinstance(self.auth_info, str):
                SubElement(
                    change, QName(NAMESPACE.NIC_CONTACT, "authInfo")
                ).text = self.auth_info
            elif isinstance(self.auth_info, AuthInfo):
                change.append(self.auth_info.get_payload())
        if self.disclose is not None:
            change.append(self.disclose.get_payload())
        if self.vat is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, "vat")).text = self.vat
        if self.ident is not None:
            change.append(self.ident.get_payload())
        if self.notify_email is not None:
            SubElement(
                change, QName(NAMESPACE.NIC_CONTACT, "notifyEmail")
            ).text = self.notify_email

        return change


@dataclass
class UpdateHost(Command):
    """EPP update host command.

    Attributes:
        name: Content of epp/command/update/update/name element.
        add: Content of epp/command/update/update/add element.
        rem: Content of epp/command/update/update/rem element.
        chg: Content of epp/command/update/update/chg/name element.
    """

    response_class = Result

    name: str
    add: Sequence[Union[Ip, HostStatus]] = field(default_factory=list)
    rem: Sequence[Union[Ip, HostStatus]] = field(default_factory=list)
    chg: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for UpdateHost.

        Returns:
            Element with a host to update.
        """
        update = Element(QName(NAMESPACE.EPP, "update"))

        host_update = SubElement(update, QName(NAMESPACE.NIC_HOST, "update"))
        host_update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_HOST
        )

        SubElement(host_update, QName(NAMESPACE.NIC_HOST, "name")).text = self.name

        add = Element(QName(NAMESPACE.NIC_HOST, "add"))
        for item in self.add:
            add.append(item.get_payload())
        if len(add):
            host_update.append(add)

        rem = Element(QName(NAMESPACE.NIC_HOST, "rem"))
        for item in self.rem:
            rem.append(item.get_payload())
        if len(rem):
            host_update.append(rem)

        if self.chg is not None:
            chg = SubElement(host_update, QName(NAMESPACE.NIC_HOST, "chg"))
            SubElement(chg, QName(NAMESPACE.NIC_HOST, "name")).text = self.chg

        return update


@dataclass
class UpdateKeyset(Command):
    """EPP update keyset command.

    Attributes:
        id: Content of epp/command/update/update/id element.
        add: Content of epp/command/update/update/add element.
        rem: Content of epp/command/update/update/rem element.
        auth_info: Content of epp/command/update/update/chg/authInfo element.
    """

    response_class = Result

    id: str
    add: Sequence[Union[Dnskey, str]] = field(default_factory=list)
    rem: Sequence[Union[Dnskey, str]] = field(default_factory=list)
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for UpdateKeyset.

        Returns:
            Element with a keyset to update.
        """
        update = Element(QName(NAMESPACE.EPP, "update"))

        keyset_update = SubElement(update, QName(NAMESPACE.NIC_KEYSET, "update"))
        keyset_update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_KEYSET
        )

        SubElement(keyset_update, QName(NAMESPACE.NIC_KEYSET, "id")).text = self.id

        add = Element(QName(NAMESPACE.NIC_KEYSET, "add"))
        for item in self.add:
            if isinstance(item, Dnskey):
                add.append(item.get_payload())
            else:
                SubElement(add, QName(NAMESPACE.NIC_KEYSET, "tech")).text = item
        if len(add):
            keyset_update.append(add)

        rem = Element(QName(NAMESPACE.NIC_KEYSET, "rem"))
        for item in self.rem:
            if isinstance(item, Dnskey):
                rem.append(item.get_payload())
            else:
                SubElement(rem, QName(NAMESPACE.NIC_KEYSET, "tech")).text = item
        if len(rem):
            keyset_update.append(rem)

        if self.auth_info is not None:
            chg = SubElement(keyset_update, QName(NAMESPACE.NIC_KEYSET, "chg"))
            SubElement(
                chg, QName(NAMESPACE.NIC_KEYSET, "authInfo")
            ).text = self.auth_info

        return update


@dataclass
class UpdateNsset(Command):
    """EPP update nsset command.

    Attributes:
        id: Content of epp/command/update/update/id element.
        add: Content of epp/command/update/update/add element.
        rem: Content of epp/command/update/update/rem element.
        auth_info: Content of epp/command/update/update/chg/authInfo element.
        reportlevel: Content of epp/command/update/update/chg/reportlevel element.
    """

    response_class = Result

    id: str
    add: Sequence[Union[Ns, str]] = field(default_factory=list)
    rem: Sequence[Union[Ns, str]] = field(default_factory=list)
    auth_info: Optional[str] = None
    reportlevel: Optional[int] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for UpdateNsset.

        Returns:
            Element with a nsset to update.
        """
        update = Element(QName(NAMESPACE.EPP, "update"))

        nsset_update = SubElement(update, QName(NAMESPACE.NIC_NSSET, "update"))
        nsset_update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_NSSET
        )

        SubElement(nsset_update, QName(NAMESPACE.NIC_NSSET, "id")).text = self.id

        add = Element(QName(NAMESPACE.NIC_NSSET, "add"))
        for item in self.add:
            if isinstance(item, Ns):
                add.append(item.get_payload())
            else:
                SubElement(add, QName(NAMESPACE.NIC_NSSET, "tech")).text = item
        if len(add):
            nsset_update.append(add)

        rem = Element(QName(NAMESPACE.NIC_NSSET, "rem"))
        for item in self.rem:
            if isinstance(item, Ns):
                SubElement(rem, QName(NAMESPACE.NIC_NSSET, "name")).text = item.name
            else:
                SubElement(rem, QName(NAMESPACE.NIC_NSSET, "tech")).text = item
        if len(rem):
            nsset_update.append(rem)

        chg = Element(QName(NAMESPACE.NIC_NSSET, "chg"))
        if self.auth_info is not None:
            SubElement(
                chg, QName(NAMESPACE.NIC_NSSET, "authInfo")
            ).text = self.auth_info
        if self.reportlevel is not None:
            SubElement(chg, QName(NAMESPACE.NIC_NSSET, "reportlevel")).text = str(
                self.reportlevel
            )

        if len(chg):
            nsset_update.append(chg)

        return update
