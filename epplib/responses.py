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
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Optional, Sequence, Union, cast

from isodate import Duration, parse_datetime, parse_duration
from lxml.etree import Element, QName, fromstring  # nosec - TODO: Fix lxml security issues

from epplib.constants import NAMESPACE_EPP

NAMESPACES = {'epp': NAMESPACE_EPP}
GreetingPayloadType = Mapping[str, Union[None, Sequence[str], Sequence['Greeting.Statement'], datetime, str, timedelta]]


class Response(ABC):
    """Base class for responses to EPP commands."""

    # Concrete Responses are supposed to be dataclasses. ABC can not be a dataclass. We need to specify init for typing.
    def __init__(self, *args, **kwargs):
        pass  # pragma: no cover

    @classmethod
    def parse(cls, raw_response: bytes) -> 'Response':
        """Parse the xml response into the dataclass.

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
        expiry: Content of the epp/greeting/expiry element.
    """

    @dataclass
    class Statement:
        """A dataclass to represent the EPP statement.

        Attributes:
            purpose: Content of the epp/greeting/statement/purpose element.
            recipient: Content of the epp/greeting/statement/recipient element.
            retention: Content of the epp/greeting/statement/retention element.
        """

        purpose: List[str]
        recipient: List[str]
        retention: Optional[str]

    sv_id: str
    sv_date: str
    versions: List[str]
    langs: List[str]
    obj_uris: List[str]
    ext_uris: List[str]
    access: str
    statements: List[Statement]
    expiry: Optional[str]

    @classmethod
    def parse(cls, *args, **kwargs) -> 'Greeting':
        """Parse the xml response into the Greeting dataclass."""
        return cast('Greeting', super().parse(*args, **kwargs))

    @classmethod
    def _parse_payload(cls, element: Element) -> GreetingPayloadType:
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
            'expiry': cls._parse_expiry(element.find('./epp:dcp/epp:expiry', namespaces=NAMESPACES))
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
        )

    @classmethod
    def _parse_expiry(cls, element: Element) -> Union[None, datetime, timedelta]:
        """Parse the expiry part of Greeting.

        Result depends on wheter the expiry is relativa or absolute. Absolute expiry is returned as datetime whereas
        relative expiry is returned as timedelta.

        Args:
            element: Expiry element of Greeting.

        Returns:
            Parsed expiry expressed as either a point in time or duration until the expiry.
        """
        if element is None:
            return None

        tag = element[0].tag
        text = element[0].text

        # TODO: Wrap parser errors into nicer exception?
        if tag == QName(NAMESPACE_EPP, 'absolute'):
            return parse_datetime(text)
        elif tag == QName(NAMESPACE_EPP, 'relative'):
            result = parse_duration(text)
            if isinstance(result, Duration):
                result = result.totimedelta(datetime.now())
            return result
        else:
            raise ValueError('Expected expiry specification. Found "{}" instead.'.format(tag))
