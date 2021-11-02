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

"""Module providing responses to EPP check commands."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import ClassVar, Mapping, Optional

from lxml.etree import Element, QName

from epplib.constants import NAMESPACE
from epplib.models import ExtraAddr
from epplib.utils import ParseXMLMixin


class ResponseExtension(ABC):
    """Base class for EPP response extension.

    Attributes:
        tag: The tag of the root element of the extension.
    """

    tag: ClassVar[QName]

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'ResponseExtension':
        """Extract the extension content from the element.

        Args:
            element: XML element containg the extension data.

        Returns:
            Dataclass representing the extension.
        """


@dataclass
class EnumInfoExtension(ParseXMLMixin, ResponseExtension):
    """Dataclass to represent CZ.NIC ENUM extension.

    Attributes:
        val_ex_date: Content of the epp/response/extension/infData/valExDate element.
        publish: Content of the epp/response/extension/infData/publish element.
        tag: The tag of the root element of the extension.
    """

    _NAMESPACES: ClassVar[Mapping[str, str]] = {
        **ParseXMLMixin._NAMESPACES,
        'enumval': NAMESPACE.NIC_ENUMVAL,
    }

    tag = QName(NAMESPACE.NIC_ENUMVAL, 'infData')

    val_ex_date: Optional[date]
    publish: Optional[bool]

    @classmethod
    def extract(cls, element: Element) -> 'EnumInfoExtension':
        """Extract the extension content from the element.

        Args:
            element: XML element containg the extension data.

        Returns:
            Dataclass representing the extension.
        """
        val_ex_date = cls._optional(cls._parse_date, cls._find_text(element, './enumval:valExDate'))
        publish = cls._optional(cls._str_to_bool, cls._find_text(element, './enumval:publish'))
        return cls(val_ex_date=val_ex_date, publish=publish)


@dataclass
class MailingAddressExtension(ParseXMLMixin, ResponseExtension):
    """Dataclass to represent CZ.NIC ENUM extension.

    Attributes:
        addr: Content of the epp/response/extension/infData/mailing/addr element.
    """

    _NAMESPACES: ClassVar[Mapping[str, str]] = {
        **ParseXMLMixin._NAMESPACES,
        'extra-addr': NAMESPACE.NIC_EXTRA_ADDR,
    }

    tag = QName(NAMESPACE.NIC_EXTRA_ADDR, 'mailing')

    addr: ExtraAddr

    @classmethod
    def extract(cls, element: Element) -> 'MailingAddressExtension':
        """Extract the extension content from the element.

        Args:
            element: XML element containg the extension data.

        Returns:
            Dataclass representing the extension.
        """
        addr = ExtraAddr.extract(cls._find(element, 'extra-addr:addr'))
        return cls(addr=addr)
