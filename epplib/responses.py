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
from typing import Any, List, Mapping, Optional, Sequence, Union, cast

from lxml.etree import Element, QName, fromstring  # nosec - TODO: Fix lxml security issues

from epplib.constants import NAMESPACE_EPP

NAMESPACES = {'epp': NAMESPACE_EPP}


class Response(ABC):
    """Base class for responses to EPP commands."""

    # Concrete Responses are supposed to be dataclasses. ABC can not be a dataclass. We need to specify init for typing.
    def __init__(self, *args, **kwargs):
        pass  # pragma: no cover

    @classmethod
    def parse(cls, raw_response: bytes) -> 'Response':
        """Parse the XML response into the dataclass.

        Args:
            raw_response: The raw XML response which will be parsed into the Response object.
        """
        root = fromstring(raw_response)

        if root.tag != QName(NAMESPACE_EPP, 'epp'):
            raise ValueError('Root element has to be "epp". Found: {}'.format(root.tag))

        payload = root[0]
        data = cls._parse_payload(payload)
        return cls(**data)

    @classmethod
    @abstractmethod
    def _parse_payload(cls, element: Element) -> Mapping[str, Any]:
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


@dataclass
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

    sv_id: str
    sv_date: str
    versions: List[str]
    langs: List[str]
    obj_uris: List[str]
    ext_uris: List[str]
    access: str
    statements: List[Statement]

    @classmethod
    def parse(cls, raw_response: bytes) -> 'Greeting':
        """Parse the xml response into the Greeting dataclass."""
        return cast('Greeting', super().parse(raw_response))

    @classmethod
    def _parse_payload(cls, element: Element) -> Mapping[str, Union[None, str, Sequence[str], Sequence[Statement]]]:
        """Parse the actual information from the response.

        Args:
            element: Child element of the epp element.
        """
        data = {
            'sv_id': cls._find_text(element, './epp:svID'),
            'sv_date': cls._find_text(element, './epp:svDate'),

            'versions': cls._find_all_text(element, './epp:svcMenu/epp:version'),
            'langs': cls._find_all_text(element, './epp:svcMenu/epp:lang'),
            'obj_uris': cls._find_all_text(element, './epp:svcMenu/epp:objURI'),

            'ext_uris': cls._find_all_text(element, './epp:svcMenu/epp:svcExtension/epp:extURI'),

            'access': cls._find_child(element, './epp:dcp/epp:access'),

            'statements': [
                cls._parse_statement(item) for item in element.findall('./epp:dcp/epp:statement', namespaces=NAMESPACES)
            ],
        }

        return data

    @classmethod
    def _parse_statement(cls, element: Element) -> Statement:
        """Parse the statement part of Greeting.

        Args:
            element: Statement element of Greeting.

        Returns:
            Parsed Statement.
        """
        return cls.Statement(
            purpose=cls._find_children(element, './epp:purpose'),
            recipient=cls._find_children(element, './epp:recipient'),
            retention=cls._find_child(element, './epp:retention'),
            expiry=cls._find_child(element, './epp:expiry')
        )
