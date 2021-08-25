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
from abc import ABC, abstractmethod, abstractproperty
from typing import Type

from lxml.etree import Element, ElementTree, QName, XMLSchema, tostring  # nosec - TODO: Fix lxml security issues

from epplib.constants import NAMESPACE_EPP, NAMESPACE_XSI, XSI_SCHEMA_LOCATION
from epplib.responses import Greeting, Response


class Request(ABC):
    """Base class for EPP requests."""

    def xml(self, schema: XMLSchema = None) -> bytes:
        """Return the XML representation of the Request.

        Returns:
            The XML representation of the Request.
        """
        root = Element(QName(NAMESPACE_EPP, 'epp'))
        root.set(QName(NAMESPACE_XSI, 'schemaLocation'), XSI_SCHEMA_LOCATION)
        root.append(self._get_payload())

        document = ElementTree(root)

        if schema is not None:
            schema.assertValid(document)

        return tostring(document, encoding='utf-8', xml_declaration=True)

    @abstractmethod
    def _get_payload(self) -> Element:
        """Create subelements of the epp tag specific for the given Request subclass.

        Returns:
            Element with the Request payload.
        """

    @abstractproperty
    def response_class(self) -> Type[Response]:
        """Class of the corresponding response."""


class Hello(Request):
    """EPP Hello."""

    response_class = Greeting

    def _get_payload(self) -> Element:
        """Create subelements of the epp tag specific for the given Request subclass.

        Returns:
            Element with the payload of the Hello command.
        """
        return Element(QName(NAMESPACE_EPP, 'hello'))
