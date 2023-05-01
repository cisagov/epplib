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

"""Module providing EPP info commands."""
from dataclasses import dataclass
from typing import Optional, Union

from lxml.etree import Element, QName, SubElement

from epplib.commands.base import Command
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import AuthInfo
from epplib.responses import InfoContactResult, InfoDomainResult, InfoHostResult, InfoKeysetResult, InfoNssetResult

class Info(Command):
    """Base class for EPP Info commands."""

    def _get_info_payload(self, namespace: str, schema_location: str,
                          tag: str, item: str, auth_info: Optional[str] = None) -> Element:
        """Create subelements specific for info command.

        Returns:
            Element with an item to query.
        """
        info = Element(QName(NAMESPACE.EPP, 'info'))

        domain_info = SubElement(info, QName(namespace, 'info'))
        domain_info.set(QName(NAMESPACE.XSI, 'schemaLocation'), schema_location)

        SubElement(domain_info, QName(namespace, tag)).text = item

        if auth_info is not None:
            if isinstance(auth_info, str):
                SubElement(domain_info, QName(namespace, 'authInfo')).text = auth_info
            elif isinstance(auth_info, AuthInfo):
                domain_info.append(auth_info.get_payload())
        return info


@dataclass
class InfoDomain(Info):
    """EPP Info Domain command.

    Attributes:
        name: Content of the epp/command/info/info/name element.
    """

    response_class = InfoDomainResult
    name: str
    auth_info: Optional[Union[str, AuthInfo]] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for InfoDomain.

        Returns:
            Element with a domain to query.
        """
        return self._get_info_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN,
                                      'name', self.name, self.auth_info)


@dataclass
class InfoContact(Info):
    """EPP Info Contact command.

    Attributes:
        id: Content of the epp/command/info/info/id element.
    """

    response_class = InfoContactResult
    id: str
    auth_info: Optional[Union[str, AuthInfo]] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for InfoContact.

        Returns:
            Element with a contact to query.
        """
        return self._get_info_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.id, self.auth_info)


@dataclass
class InfoHost(Info):
    """EPP Info Domain command.

    Attributes:
        name: Content of the epp/command/info/info/name element.
    """

    response_class = InfoHostResult
    name: str

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for InfoHost.

        Returns:
            Element with a host to query.
        """
        return self._get_info_payload(NAMESPACE.NIC_HOST, SCHEMA_LOCATION.NIC_HOST, 'name', self.name)


@dataclass
class InfoKeyset(Info):
    """EPP Info Keyset command.

    Attributes:
        id: Content of the epp/command/info/info/id element.
    """

    response_class = InfoKeysetResult
    id: str
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for InfoKeyset.

        Returns:
            Element with a keyset to query.
        """
        return self._get_info_payload(NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, 'id', self.id, self.auth_info)


@dataclass
class InfoNsset(Info):
    """EPP Info Nsset command.

    Attributes:
        id: Content of the epp/command/info/info/id element.
    """

    response_class = InfoNssetResult
    id: str
    auth_info: Optional[str] = None

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for InfoNsset.

        Returns:
            Element with a nsset to query.
        """
        return self._get_info_payload(NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, 'id', self.id, self.auth_info)
