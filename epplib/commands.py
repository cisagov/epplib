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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional, Sequence, Type

from lxml.etree import Element, ElementTree, QName, SubElement, XMLSchema, tostring

from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import (CheckContactResult, CheckDomainResult, CheckKeysetResult, CheckNssetResult, Greeting,
                              Response, Result)


class Request(ABC):
    """Base class for EPP requests."""

    response_class: ClassVar[Type[Response]]

    def xml(self, tr_id: str = None, schema: XMLSchema = None) -> bytes:
        """Return the XML representation of the Request.

        Returns:
            The XML representation of the Request.
        """
        root = Element(QName(NAMESPACE.EPP, 'epp'))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.XSI)
        root.append(self._get_payload(tr_id=tr_id))

        document = ElementTree(root)

        if schema is not None:
            schema.assertValid(document)

        return tostring(document, encoding='utf-8', xml_declaration=True)

    @abstractmethod
    def _get_payload(self, tr_id: Optional[str]) -> Element:
        """Create subelements of the epp tag specific for the given Request subclass.

        Returns:
            Element with the Request payload.
        """


class Hello(Request):
    """EPP Hello."""

    response_class = Greeting

    def _get_payload(self, tr_id: Optional[str]) -> Element:
        """Create subelements of the epp tag specific for the given Request subclass.

        Returns:
            Element with the payload of the Hello command.
        """
        return Element(QName(NAMESPACE.EPP, 'hello'))


class Command(Request):
    """Base class for EPP Commands."""

    def _get_payload(self, tr_id: str = None) -> Element:
        """Create subelements of the epp tag specific for the given Command.

        Returns:
            Element with the Command payload.
        """
        command_element = Element(QName(NAMESPACE.EPP, 'command'))
        command_element.append(self._get_command_payload())
        if tr_id is not None:
            SubElement(command_element, QName(NAMESPACE.EPP, 'clTRID')).text = tr_id
        return command_element

    @abstractmethod
    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for the given Command subclass.

        Returns:
            Element with the Command specific payload.
        """


@dataclass
class Login(Command):
    """EPP Login command.

    Attributes:
        cl_id: EPP clID
        password: EPP pw
        new_password: EPP newPW
        version: EPP options/version
        lang: EPP options/lang
        obj_uris: EPP/svcs/objURI
        ext_uris: EPP/svcs/svcExtension/extURI
    """

    response_class = Result

    cl_id: str
    password: str
    obj_uris: List[str]
    new_password: Optional[str] = None
    version: str = '1.0'
    lang: str = 'en'
    ext_uris: List[str] = field(default_factory=list)

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for Login.

        Returns:
            Element with the Login specific payload.
        """
        root = Element(QName(NAMESPACE.EPP, 'login'))

        SubElement(root, QName(NAMESPACE.EPP, 'clID')).text = self.cl_id
        SubElement(root, QName(NAMESPACE.EPP, 'pw')).text = self.password
        if self.new_password is not None:
            SubElement(root, QName(NAMESPACE.EPP, 'newPW')).text = self.new_password

        options = SubElement(root, QName(NAMESPACE.EPP, 'options'))
        SubElement(options, QName(NAMESPACE.EPP, 'version')).text = self.version
        SubElement(options, QName(NAMESPACE.EPP, 'lang')).text = self.lang

        svcs = SubElement(root, QName(NAMESPACE.EPP, 'svcs'))
        for uri in self.obj_uris:
            SubElement(svcs, QName(NAMESPACE.EPP, 'objURI')).text = uri

        if len(self.ext_uris) > 0:
            svc_extension = SubElement(svcs, QName(NAMESPACE.EPP, 'svcExtension'))
            for uri in self.ext_uris:
                SubElement(svc_extension, QName(NAMESPACE.EPP, 'extURI')).text = uri

        return root


@dataclass
class Logout(Command):
    """EPP Logout command."""

    response_class = Result

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for Logout.

        Returns:
            Element with the Logout specific payload.
        """
        return Element(QName(NAMESPACE.EPP, 'logout'))


class Check(Command):
    """Base class for EPP Check commands."""

    def _get_check_payload(self, namespace: str, schema_location: str, tag: str, items: Sequence[str]) -> Element:
        """Create subelements of the command tag specific for the Check command.

        Returns:
            Element with a list of items to check.
        """
        root = Element(QName(NAMESPACE.EPP, 'check'))

        item_check = SubElement(root, QName(namespace, 'check'))
        item_check.set(QName(NAMESPACE.XSI, 'schemaLocation'), schema_location)
        for item in items:
            SubElement(item_check, QName(namespace, tag)).text = item

        return root


@dataclass
class CheckDomain(Check):
    """EPP Domain Check command.

    Attributes:
        domains: List of domains to check.
    """

    response_class = CheckDomainResult
    domains: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckDomain.

        Returns:
            Element with a list of domains to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_DOMAIN, SCHEMA_LOCATION.NIC_DOMAIN, 'name', self.domains)


@dataclass
class CheckContact(Check):
    """EPP Check contact command.

    Attributes:
        contacts: List of contacts to check.
    """

    response_class = CheckContactResult

    contacts: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckContact.

        Returns:
            Element with a list of contacts to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_CONTACT, SCHEMA_LOCATION.NIC_CONTACT, 'id', self.contacts)


@dataclass
class CheckNsset(Check):
    """EPP Check nsset command.

    Attributes:
        nssets: List of nssets to check.
    """

    response_class = CheckNssetResult

    nssets: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckNsset.

        Returns:
            Element with a list of nssets to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_NSSET, SCHEMA_LOCATION.NIC_NSSET, 'id', self.nssets)


@dataclass
class CheckKeyset(Check):
    """EPP Check keyset command.

    Attributes:
        keysets: List of keysets to check.
    """

    response_class = CheckKeysetResult

    keysets: List[str]

    def _get_command_payload(self) -> Element:
        """Create subelements of the command tag specific for CheckKeyset.

        Returns:
            Element with a list of keysets to check.
        """
        return self._get_check_payload(NAMESPACE.NIC_KEYSET, SCHEMA_LOCATION.NIC_KEYSET, 'id', self.keysets)
