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

"""Module providing base EPP commands."""
from abc import abstractmethod
from dataclasses import dataclass

from lxml.etree import Element, QName, SubElement

from epplib.commands import Request
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import CreditInfoResult, Result


class Extension(Request):
    """Base class for EPP Extensions."""

    def _get_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the epp tag specific for the given Command.

        Returns:
            Element with the Extension payload.
        """
        extension_element = Element(QName(NAMESPACE.EPP, 'extension'))
        extension_element.append(self._get_extension_payload(tr_id))

        return extension_element

    @abstractmethod
    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for the given Extension subclass.

        Returns:
            Element with the Extension specific payload.
        """


class FredExtCommand(Extension):
    """Base class for Fred ext commands."""

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for Fred ext command.

        Returns:
            Element with the Fred ext command payload.
        """
        root = Element(QName(NAMESPACE.FRED, 'extcommand'))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.FRED)
        SubElement(root, QName(NAMESPACE.FRED, 'clTRID')).text = tr_id

        return root


class CreditInfoRequest(FredExtCommand):
    """Fred credit info request EPP Extension."""

    response_class = CreditInfoResult

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for Credit info request.

        Returns:
            Element with Credit info request payload.
        """
        root = super()._get_extension_payload(tr_id)
        root.insert(0, Element(QName(NAMESPACE.FRED, 'creditInfo')))

        return root


@dataclass
class SendAuthInfoDomain(Extension):
    """Fred send auth info for domain EPP Extension."""

    response_class = Result
    name: str

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        root = Element(QName(NAMESPACE.FRED, 'extcommand'))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.FRED)
        fred_auth_info = SubElement(root, QName(NAMESPACE.FRED, 'sendAuthInfo'))
        domain_auth_info = SubElement(fred_auth_info, QName(NAMESPACE.NIC_DOMAIN, 'sendAuthInfo'))
        domain_auth_info.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_DOMAIN)
        SubElement(domain_auth_info, QName(NAMESPACE.NIC_DOMAIN, 'name')).text = self.name
        SubElement(root, QName(NAMESPACE.FRED, 'clTRID')).text = tr_id

        return root
