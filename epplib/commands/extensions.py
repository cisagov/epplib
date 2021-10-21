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

"""Module providing extensions to EPP commands."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional

from lxml.etree import Element, QName, SubElement

from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import ExtraAddr


class CommandExtension(ABC):
    """Base class for Command extensions."""

    @abstractmethod
    def get_payload(self) -> Element:
        """Create EPP Elements specific to the given Extension."""


@dataclass
class CreateDomainEnumExtension(CommandExtension):
    """ENUM extension for Create Domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element
        publish: Content of extension/create/publish element
    """

    val_ex_date: Optional[date] = None
    publish: Optional[bool] = None

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateDomainEnumExtension."""
        create = Element(QName(NAMESPACE.NIC_ENUMVAL, 'create'))
        create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_ENUMVAL)
        if self.val_ex_date is not None:
            expiration_date = SubElement(create, QName(NAMESPACE.NIC_ENUMVAL, 'valExDate'))
            expiration_date.text = str(self.val_ex_date)
        if self.publish is not None:
            SubElement(create, QName(NAMESPACE.NIC_ENUMVAL, 'publish')).text = str(self.publish).lower()
        return create


@dataclass
class CreateContactMailingAddressExtension(CommandExtension):
    """Mailing address extension for Create command command.

    Attributes:
        addr: Content of extension/create/mailing/addr element
    """

    addr: ExtraAddr

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateContactMailingAddressExtension."""
        create = Element(QName(NAMESPACE.NIC_EXTRA_ADDR, 'create'))
        create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_EXTRA_ADDR)
        mailing = SubElement(create, QName(NAMESPACE.NIC_EXTRA_ADDR, 'mailing'))
        mailing.append(self.addr.get_payload())
        return create
