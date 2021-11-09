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
from dataclasses import dataclass, field
from typing import Optional, Sequence

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


class SendAuthInfo(Extension):
    """Base class for Fred send auth info EPP Extension."""

    response_class = Result

    def _get_auth_info_payload(self, namespace: str, location: str, tag: str, item: str, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        root = Element(QName(NAMESPACE.FRED, 'extcommand'))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.FRED)
        fred_auth_info = SubElement(root, QName(NAMESPACE.FRED, 'sendAuthInfo'))
        domain_auth_info = SubElement(fred_auth_info, QName(namespace, 'sendAuthInfo'))
        domain_auth_info.set(QName(NAMESPACE.XSI, 'schemaLocation'), location)
        SubElement(domain_auth_info, QName(namespace, tag)).text = item
        SubElement(root, QName(NAMESPACE.FRED, 'clTRID')).text = tr_id

        return root


@dataclass
class TestNsset(FredExtCommand):
    """Test Nsset EPP Extension command."""

    response_class = Result

    id: str
    level: Optional[int] = None
    names: Sequence[str] = field(default_factory=list)

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for test nsset.

        Returns:
            Element with test nsset request payload.
        """
        root = super()._get_extension_payload(tr_id)
        fred_test = Element(QName(NAMESPACE.FRED, 'test'))
        root.insert(0, fred_test)

        nsset_test = SubElement(fred_test, QName(NAMESPACE.NIC_NSSET, 'test'))
        nsset_test.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_NSSET)
        SubElement(nsset_test, QName(NAMESPACE.NIC_NSSET, 'id')).text = self.id
        if self.level is not None:
            SubElement(nsset_test, QName(NAMESPACE.NIC_NSSET, 'level')).text = str(self.level)
        for item in self.names:
            SubElement(nsset_test, QName(NAMESPACE.NIC_NSSET, 'name')).text = item

        return root


@dataclass
class SendAuthInfoContact(SendAuthInfo):
    """Fred send auth info for contact EPP Extension."""

    response_class = Result
    id: str

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        return self._get_auth_info_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.id, tr_id)


@dataclass
class SendAuthInfoDomain(SendAuthInfo):
    """Fred send auth info for domain EPP Extension."""

    response_class = Result
    name: str

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        return self._get_auth_info_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, 'name', self.name, tr_id)


@dataclass
class SendAuthInfoKeyset(SendAuthInfo):
    """Fred send auth info for keyset EPP Extension."""

    response_class = Result
    id: str

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        return self._get_auth_info_payload(NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, 'id', self.id, tr_id)


@dataclass
class SendAuthInfoNsset(SendAuthInfo):
    """Fred send auth info for nsset EPP Extension."""

    response_class = Result
    id: str

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the extension tag specific for send auth info.

        Returns:
            Element with send auth info request payload.
        """
        return self._get_auth_info_payload(NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, 'id', self.id, tr_id)
