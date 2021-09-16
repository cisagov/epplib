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
from datetime import date
from typing import Optional

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION, Unit
from epplib.responses import CreateDomainResult


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
        authInfo: authInfo for domain transfers
    """

    response_class = CreateDomainResult

    name: str
    registrant: str
    period: Optional[int] = None
    unit: Unit = Unit.YEAR
    nsset: Optional[str] = None
    keyset: Optional[str] = None
    admin: Optional[str] = None
    authInfo: Optional[str] = None

    enumval_val_expiration_date: Optional[date] = None
    enumval_publish: Optional[bool] = None

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
        if self.authInfo is not None:
            SubElement(domain_create, QName(NAMESPACE.NIC_DOMAIN, 'authInfo')).text = self.authInfo

        return create

    def _get_extension_payload(self) -> Optional[Element]:
        create = Element(QName(NAMESPACE.NIC_ENUMVAL, 'create'))
        create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_ENUMVAL)
        if self.enumval_val_expiration_date is not None:
            expiration_date = SubElement(create, QName(NAMESPACE.NIC_ENUMVAL, 'valExDate'))
            expiration_date.text = str(self.enumval_val_expiration_date)
        if self.enumval_publish is not None:
            SubElement(create, QName(NAMESPACE.NIC_ENUMVAL, 'publish')).text = str(self.enumval_publish).lower()

        if len(create) > 0:
            return create
        else:
            return None
