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

"""Module providing means to process responses to EPP commands."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from lxml.etree import Element, QName, fromstring  # nosec - TODO: Fix lxml security issues

from epplib.constants import NAMESPACE_EPP

NAMESPACES = {'epp': NAMESPACE_EPP}


class Response(ABC):
    """Base class for responses to EPP commands.

    Args:
        raw_response: The raw XML response which will be parsed into the Response object.
    """

    def __init__(self, raw_response: bytes):
        root = fromstring(raw_response)

        if root.tag != QName(NAMESPACE_EPP, 'epp'):
            raise ValueError('Root element has to be "epp". Found: {}'.format(root.tag))

        payload = root[0]
        self._parse_payload(payload)

    @abstractmethod
    def _parse_payload(self, element: Element) -> None:
        """Parse the actual information from the response.

        Args:
            element: Child element of the epp element.
        """

    @staticmethod
    def _find_text(element: Element, path: str) -> str:
        return element.findtext(path, namespaces=NAMESPACES)

    @staticmethod
    def _find_all_text(element: Element, path: str) -> List[str]:
        return [(elem.text or '') for elem in element.findall(path, namespaces=NAMESPACES)]

    @staticmethod
    def _find_child(element: Element, path: str) -> Optional[str]:
        found_tags = Response._find_children(element, path)
        if len(found_tags) > 0:
            return found_tags[0]
        else:
            return None

    @staticmethod
    def _find_children(element: Element, path: str) -> List[str]:
        nodes = element.findall(path + '/*', namespaces=NAMESPACES)
        return [QName(item.tag).localname for item in nodes]


# TODO: Make it a data class - move params to init
class Greeting(Response):
    """EPP Greeting representation.

    Attributes:
        sv_id: Content of the epp/greeting/svID element.
        sv_date: Content of the epp/greeting/svDate element.
        versions: Content of the epp/greeting/svcMenu/version element.
        langs: Content of the epp/greeting/svcMenu/lang element.
        obj_uris: Content of the epp/greeting/svcMenu/objURI element.
        ext_uris: Content of the epp/greeting/svcMenu/svcExtension/extURI element.
        access: Content of the epp/greeting/dcp/access element.
        statements: Content of the epp/greeting/statement element.
    """

    @dataclass
    class Statement:
        """A dataclass to represent the EPP statement.

        Attributes:
            purpose: Content of the epp/greeting/statement/purpose element.
            recipient: Content of the epp/greeting/statement/recipient element.
            retention: Content of the epp/greeting/statement/retention element.
            expiry: Content of the epp/greeting/statement/expiry element.
        """

        purpose: List[str]
        recipient: List[str]
        retention: Optional[str]
        expiry: Optional[str]

    def _parse_payload(self, element: Element) -> None:
        """Parse the actual information from the response.

        Args:
            element: Child element of the epp element.
        """
        self.sv_id = self._find_text(element, './epp:svID')
        self.sv_date = self._find_text(element, './epp:svDate')

        self.versions = self._find_all_text(element, './epp:svcMenu/epp:version')
        self.langs = self._find_all_text(element, './epp:svcMenu/epp:lang')
        self.obj_uris = self._find_all_text(element, './epp:svcMenu/epp:objURI')

        self.ext_uris = self._find_all_text(element, './epp:svcMenu/epp:svcExtension/epp:extURI')

        self.access = self._find_child(element, './epp:dcp/epp:access')

        self.statements = [
            self._parse_statement(item) for item in element.findall('./epp:dcp/epp:statement', namespaces=NAMESPACES)
        ]

    def _parse_statement(self, element: Element) -> Statement:
        """Parse the statement part of Greeting.

        Args:
            element: Statement element of Greeting.

        Returns:
            Parsed Statement.
        """
        return self.Statement(
            purpose=self._find_children(element, './epp:purpose'),
            recipient=self._find_children(element, './epp:recipient'),
            retention=self._find_child(element, './epp:retention'),
            expiry=self._find_child(element, './epp:expiry')
        )
