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

"""Module providing EPP update commands."""
from dataclasses import dataclass, field
from typing import Optional, Sequence

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import Disclose, Ident, PostalInfo
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
    """

    response_class = Result

    name: str
    add: Sequence[str] = field(default_factory=list)
    rem: Sequence[str] = field(default_factory=list)
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    registrant: Optional[str] = None
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for UpdateDomain.

        Returns:
            Element with a domain to update.
        """
        update = Element(QName(NAMESPACE.EPP, 'update'))

        domain_update = SubElement(update, QName(NAMESPACE.NIC_DOMAIN, 'update'))
        domain_update.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)

        SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name

        if self.add:
            add = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'add'))
            for item in self.add:
                SubElement(add, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = item

        if self.rem:
            rem = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'rem'))
            for item in self.rem:
                SubElement(rem, QName(NAMESPACE.NIC_DOMAIN, 'admin')).text = item

        if self.nsset or self.keyset or self.registrant or self.auth_info:
            chg = SubElement(domain_update, QName(NAMESPACE.NIC_DOMAIN, 'chg'))
            if self.nsset is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'nsset')).text = self.nsset
            if self.keyset is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'keyset')).text = self.keyset
            if self.registrant is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'registrant')).text = self.registrant
            if self.auth_info is not None:
                SubElement(chg, QName(NAMESPACE.NIC_DOMAIN, 'authInfo')).text = self.auth_info

        return update


@dataclass
class UpdateContact(Command):
    """EPP update contact command.

    Attributes:
        id: Content of epp/command/update/update/id tag.
        postal_info: Content of epp/command/update/update/chg/postalInfo tag.
        voice: Content of epp/command/update/update/chg/voice tag.
        fax: Content of epp/command/update/update/chg/fax tag.
        email: Content of epp/command/update/update/chg/email tag.
        auth_info: Content of epp/command/update/update/chg/authInfo tag.
        disclose: Content of epp/command/update/update/chg/disclose tag.
        vat: Content of epp/command/update/update/chg/vat tag.
        ident: Content of epp/command/update/update/chg/ident tag.
        notify_email: Content of epp/command/update/update/chg/notifyEmail tag.
    """

    response_class = Result

    id: str
    postal_info: Optional[PostalInfo] = None
    voice: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    auth_info: Optional[str] = None
    disclose: Optional[Disclose] = None
    vat: Optional[str] = None
    ident: Optional[Ident] = None
    notify_email: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for UpdateContact.

        Returns:
            Element with a contact to update.
        """
        update = Element(QName(NAMESPACE.EPP, 'update'))

        contact_update = SubElement(update, QName(NAMESPACE.NIC_CONTACT, 'update'))
        contact_update.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_CONTACT)

        SubElement(contact_update, QName(NAMESPACE.NIC_CONTACT, 'id')).text = self.id

        change = self._get_change()
        if len(change):
            contact_update.append(change)

        return update

    def _get_change(self) -> Element:
        """Create chg element and its subelements.

        Returns:
            Element with the chg element.
        """
        change = Element(QName(NAMESPACE.NIC_CONTACT, 'chg'))

        if self.postal_info is not None:
            change.append(self.postal_info.get_payload())
        if self.voice is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'voice')).text = self.voice
        if self.fax is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'fax')).text = self.fax
        if self.email is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'email')).text = self.email
        if self.auth_info is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'authInfo')).text = self.auth_info
        if self.disclose is not None:
            change.append(self.disclose.get_payload())
        if self.vat is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'vat')).text = self.vat
        if self.ident is not None:
            change.append(self.ident.get_payload())
        if self.notify_email is not None:
            SubElement(change, QName(NAMESPACE.NIC_CONTACT, 'notifyEmail')).text = self.notify_email

        return change
