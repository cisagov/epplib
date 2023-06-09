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

"""Module providing base EPP commands."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional, Sequence, Type, cast

from lxml.etree import Element, ElementTree, QName, SubElement, XMLSchema, tostring

from epplib.commands.command_extensions import CommandExtension
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import Greeting, Response, Result


class Request(ABC):
    """Base class for EPP requests."""

    response_class: ClassVar[Type[Response]]

    def xml(
        self, tr_id: Optional[str] = None, schema: Optional[XMLSchema] = None
    ) -> bytes:
        """Return the XML representation of the Request.

        Returns:
            The XML representation of the Request.
        """
        root = Element(QName(NAMESPACE.EPP, "epp"))
        root.set(QName(NAMESPACE.XSI, "schemaLocation"), SCHEMA_LOCATION.XSI)
        root.append(self._get_payload(tr_id=tr_id))

        document = ElementTree(root)

        if schema is not None:
            schema.assertValid(document)

        return cast(bytes, tostring(document, encoding="utf-8", xml_declaration=True))

    @abstractmethod
    def _get_payload(self, tr_id: Optional[str]) -> Element:
        """Create subelements of the epp element specific for the given Request subclass.

        Returns:
            Element with the Request payload.
        """


class Hello(Request):
    """EPP Hello."""

    response_class = Greeting

    def _get_payload(self, tr_id: Optional[str]) -> Element:
        """Create subelements of the epp element specific for the given Request subclass.

        Returns:
            Element with the payload of the Hello command.
        """
        return Element(QName(NAMESPACE.EPP, "hello"))


class Command(Request):
    """Base class for EPP Commands."""

    def __post_init__(self) -> None:
        self.extensions: List[CommandExtension] = []

    def add_extension(self, extension: CommandExtension) -> None:
        """Add extension to the EPP Command.

        Args:
            extension: Extension to be added.
        """
        self.extensions.append(extension)

    def _get_payload(self, tr_id: Optional[str] = None) -> Element:
        """Create subelements of the epp element specific for the given Command.

        Returns:
            Element with the Command payload.
        """
        command_element = Element(QName(NAMESPACE.EPP, "command"))
        command_element.append(self._get_command_payload())

        extension_payload = self._get_extension_payload()
        if extension_payload:
            extension_tag = Element(QName(NAMESPACE.EPP, "extension"))
            extension_tag.extend(extension_payload)
            command_element.append(extension_tag)

        if tr_id is not None:
            SubElement(command_element, QName(NAMESPACE.EPP, "clTRID")).text = tr_id
        return command_element

    @abstractmethod
    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for the given Command subclass.

        Returns:
            Element with the Command specific payload.
        """

    def _get_extension_payload(self) -> Sequence[Element]:
        """Create extension subelements of the command element specific to the given Command subclass.

        Returns:
            Elements with the extension payload.
        """
        return [extension.get_payload() for extension in self.extensions]


@dataclass
class Login(Command):
    """EPP Login command.

    Attributes:
        cl_id: Content of the epp/command/login/clID element.
        password: Content of the epp/command/login/pw element.
        new_pw: Content of the epp/command/login/newPW element.
        version: Content of the epp/command/login/options/version element.
        lang: Content of the epp/command/login/options/lang element.
        obj_uris: Content of the epp/command/login/svcs/objURI element.
        ext_uris: Content of the epp/command/login/svcs/svcExtension/extURI element.
    """

    response_class = Result

    cl_id: str
    password: str
    obj_uris: List[str]
    new_pw: Optional[str] = None
    version: str = "1.0"
    lang: str = "en"
    ext_uris: List[str] = field(default_factory=list)

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for Login.

        Returns:
            Element with the Login specific payload.
        """
        root = Element(QName(NAMESPACE.EPP, "login"))

        SubElement(root, QName(NAMESPACE.EPP, "clID")).text = self.cl_id
        SubElement(root, QName(NAMESPACE.EPP, "pw")).text = self.password
        if self.new_pw is not None:
            SubElement(root, QName(NAMESPACE.EPP, "newPW")).text = self.new_pw

        options = SubElement(root, QName(NAMESPACE.EPP, "options"))
        SubElement(options, QName(NAMESPACE.EPP, "version")).text = self.version
        SubElement(options, QName(NAMESPACE.EPP, "lang")).text = self.lang

        svcs = SubElement(root, QName(NAMESPACE.EPP, "svcs"))
        for uri in self.obj_uris:
            SubElement(svcs, QName(NAMESPACE.EPP, "objURI")).text = uri

        if len(self.ext_uris) > 0:
            svc_extension = SubElement(svcs, QName(NAMESPACE.EPP, "svcExtension"))
            for uri in self.ext_uris:
                SubElement(svc_extension, QName(NAMESPACE.EPP, "extURI")).text = uri

        return root


@dataclass
class Logout(Command):
    """EPP Logout command."""

    response_class = Result

    def _get_command_payload(self) -> Element:
        """Create subelements of the command element specific for Logout.

        Returns:
            Element with the Logout specific payload.
        """
        return Element(QName(NAMESPACE.EPP, "logout"))
