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

"""Module providing EPP command extensions."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import ClassVar, Optional

from lxml.etree import Element, QName, SubElement

from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import ExtraAddr


class CommandExtension(ABC):
    """Base class for Command extensions."""

    @abstractmethod
    def get_payload(self) -> Element:
        """Create EPP Elements specific to the given Extension."""


@dataclass
class CreateContactMailingAddressExtension(CommandExtension):
    """Mailing address extension for Create contact command.

    Attributes:
        addr: Content of extension/create/mailing/addr element.
    """

    addr: ExtraAddr

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateContactMailingAddressExtension."""
        create = Element(QName(NAMESPACE.NIC_EXTRA_ADDR, "create"))
        create.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_EXTRA_ADDR
        )
        mailing = SubElement(create, QName(NAMESPACE.NIC_EXTRA_ADDR, "mailing"))
        mailing.append(self.addr.get_payload())
        return create


@dataclass
class UpdateContactMailingAddressExtension(CommandExtension):
    """Mailing address extension for Update contact command.

    Attributes:
        addr: If set it makes the content of extension/update/set/mailing/addr element
              if None it causes extension/update/rem/mailing element to appear
    """

    addr: Optional[ExtraAddr]

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateContactMailingAddressExtension."""
        update = Element(QName(NAMESPACE.NIC_EXTRA_ADDR, "update"))
        update.set(
            QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_EXTRA_ADDR
        )

        if self.addr is None:
            action = SubElement(update, QName(NAMESPACE.NIC_EXTRA_ADDR, "rem"))
            SubElement(action, QName(NAMESPACE.NIC_EXTRA_ADDR, "mailing"))
        else:
            action = SubElement(update, QName(NAMESPACE.NIC_EXTRA_ADDR, "set"))
            mailing = SubElement(action, QName(NAMESPACE.NIC_EXTRA_ADDR, "mailing"))
            mailing.append(self.addr.get_payload())
        return update


@dataclass
class EnumExtension(CommandExtension):
    """ENUM extension for Create Domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag: ClassVar[str]

    val_ex_date: Optional[date] = None
    publish: Optional[bool] = None

    def get_payload(self) -> Element:
        """Create EPP Elements specific to DomainEnumExtension."""
        root = Element(QName(NAMESPACE.NIC_ENUMVAL, self.tag))
        root.set(QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_ENUMVAL)
        if self.val_ex_date is not None:
            expiration_date = SubElement(
                root, QName(NAMESPACE.NIC_ENUMVAL, "valExDate")
            )
            expiration_date.text = str(self.val_ex_date)
        if self.publish is not None:
            SubElement(root, QName(NAMESPACE.NIC_ENUMVAL, "publish")).text = str(
                self.publish
            ).lower()
        return root


@dataclass
class CreateDomainEnumExtension(EnumExtension):
    """ENUM extension for Create domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag = "create"


@dataclass
class RenewDomainEnumExtension(EnumExtension):
    """ENUM extension for Renew domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag = "renew"


@dataclass
class UpdateDomainEnumExtension(EnumExtension):
    """ENUM extension for Update Domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element
        publish: Content of extension/create/publish element
    """

    tag = "update"

    def get_payload(self) -> Element:
        """Create EPP Elements specific to UpdateDomainEnumExtension."""
        root = Element(QName(NAMESPACE.NIC_ENUMVAL, self.tag))
        root.set(QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.NIC_ENUMVAL)
        change = SubElement(root, QName(NAMESPACE.NIC_ENUMVAL, "chg"))
        if self.val_ex_date is not None:
            expiration_date = SubElement(
                change, QName(NAMESPACE.NIC_ENUMVAL, "valExDate")
            )
            expiration_date.text = str(self.val_ex_date)
        if self.publish is not None:
            SubElement(change, QName(NAMESPACE.NIC_ENUMVAL, "publish")).text = str(
                self.publish
            ).lower()
        return root
