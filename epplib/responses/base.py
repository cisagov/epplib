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

"""Module providing base classes to EPP command responses."""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import (Any, Callable, ClassVar, Generic, List, Mapping, Optional, Pattern, Sequence, Type, TypeVar, Union,
                    cast)

from dateutil.parser import parse as parse_datetime
from dateutil.relativedelta import relativedelta
from lxml.etree import Element, QName, XMLSchema

from epplib.constants import NAMESPACE
from epplib.utils import safe_parse

NAMESPACES = {
    'epp': NAMESPACE.EPP,
    'contact': NAMESPACE.NIC_CONTACT,
    'domain': NAMESPACE.NIC_DOMAIN,
    'keyset': NAMESPACE.NIC_KEYSET,
    'nsset': NAMESPACE.NIC_NSSET,
}

GreetingPayload = Mapping[str, Union[None, Sequence[str], Sequence['Greeting.Statement'], datetime, relativedelta, str]]

T = TypeVar('T', bound='ResultData')
U = TypeVar('U')
N = TypeVar('N')


class ParsingError(Exception):
    """Error to indicate a failure while parsing of the EPP response."""

    def __init__(self, *args, raw_response: Any = None):
        self.raw_response = raw_response
        super().__init__(*args)

    def __str__(self):
        if self.raw_response is None:
            appendix = ''
        else:
            appendix = 'Raw response:\n{!r}'.format(self.raw_response)
        return super().__str__() + appendix


class ParseXMLMixin:
    """Mixin to simplify XML parsing."""

    duration_regex: ClassVar[Pattern] = re.compile(
        (
            r'^(?P<sign>-)?P(?P<years>\d+Y)?(?P<months>\d+M)?(?P<days>\d+D)?'
            r'(T'
            r'(?P<hours>\d+H)?(?P<minutes>\d+M)?'
            r'((?P<seconds>\d+)(?P<microseconds>\.\d+)?S)?'
            r')?$'
        ),
        re.ASCII
    )

    @staticmethod
    def _find_all(element: Element, path: str) -> List[Element]:
        return element.findall(path, namespaces=NAMESPACES)

    @staticmethod
    def _find_text(element: Element, path: str) -> str:
        return element.findtext(path, namespaces=NAMESPACES)

    @staticmethod
    def _find_all_text(element: Element, path: str) -> List[str]:
        return [(elem.text or '') for elem in element.findall(path, namespaces=NAMESPACES)]

    @staticmethod
    def _find_attrib(element: Element, path: str, attrib: str) -> Optional[str]:
        found = element.find(path, namespaces=NAMESPACES)
        if found is not None:
            return found.attrib.get(attrib)
        else:
            return None

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

    @staticmethod
    def _optional(function: Callable[[str], U], param: Optional[str]) -> Optional[U]:
        """Return function(param) if param is not None otherwise return None."""
        if param is None:
            return None
        else:
            return function(param)

    @staticmethod
    def _parse_date(value: str) -> date:
        return parse_datetime(value).date()

    @classmethod
    def _parse_duration(cls, value: str) -> relativedelta:
        """Parse duration in the 'PnYnMnDTnHnMnS' form.

        Args:
            value: String to be parsed.

        Returns:
            Duration expressed as relativedelta.

        Raises:
            ValueError: If the value can not be parsed.
        """
        value = value.strip()
        match = cls.duration_regex.fullmatch(value)
        if match:
            groups = match.groupdict()
            sign = -1 if groups.pop('sign') else 1

            seconds = groups.pop('seconds', None)
            microseconds = groups.pop('microseconds', None)

            params = {k: int(v[:-1]) for k, v in groups.items() if v is not None}
            params['seconds'] = int(seconds) if seconds is not None else 0
            params['microseconds'] = int(10**6 * float(microseconds)) if microseconds is not None else 0
            return sign * relativedelta(**params)  # type: ignore
        else:
            raise ValueError('Can not parse string "{}" as duration.'.format(value))

    @staticmethod
    def _str_to_bool(value: Optional[str]) -> Optional[bool]:
        """Convert str '0' or '1' to the corresponding bool value."""
        if value is None:
            return None
        elif value == '1':
            return True
        elif value == '0':
            return False
        else:
            raise ValueError('Value "{}" is not in the list of known boolean values.'.format(value))


class Response(ParseXMLMixin, ABC):
    """Base class for responses to EPP commands.

    Attributes:
        tag: Expected tag enclosing the response payload.
    """

    _payload_tag: ClassVar[QName]

    # Concrete Responses are supposed to be dataclasses. ABC can not be a dataclass. We need to specify init for typing.
    def __init__(self, *args, **kwargs):
        pass  # pragma: no cover

    @classmethod
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'Response':
        """Parse the xml response into the dataclass.

        Args:
            raw_response: The raw XML response which will be parsed into the Response object.
            schema: A XML schema used to validate the parsed Response. No validation is done if schema is None.

        Returns:
            Dataclass representing the EPP response.

        Raises:
            ValueError: If the root tag is not "epp" or if the tag representing the type of the response is not the one
                expected by the parser.
            ParsingError: If parsing fails for whatever reason. ParsingError wraps the original exceptions and adds the
                raw data received from the server to ease the debugging.
        """
        root = safe_parse(raw_response)

        if schema is not None:
            schema.assertValid(root)

        if root.tag != QName(NAMESPACE.EPP, 'epp'):
            raise ValueError('Root element has to be "epp". Found: {}'.format(root.tag))

        payload = root[0]
        if payload.tag != cls._payload_tag:
            raise ValueError('Expected {} tag. Found {} instead.'.format(cls._payload_tag, payload.tag))
        try:
            data = cls._extract_payload(payload)
        except Exception as exception:
            raise ParsingError(raw_response=raw_response) from exception

        return cls(**data)

    @classmethod
    @abstractmethod
    def _extract_payload(cls, element: Element) -> Mapping[str, Any]:
        """Extract the actual information from the response.

        Args:
            element: Child element of the epp element.
        """


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

    _payload_tag: ClassVar = QName(NAMESPACE.EPP, 'greeting')

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
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'Greeting':
        """Parse the xml response into the Greeting dataclass.

        Args:
            raw_response: The raw XML response which will be parsed into the Response object.
            schema: A XML schema used to validate the parsed Response. No validation is done if schema is None.
        """
        return cast('Greeting', super().parse(raw_response, schema))

    @classmethod
    def _extract_payload(cls, element: Element) -> GreetingPayload:
        """Extract the actual information from the response.

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
                cls._extract_statement(item) for item in element.findall(
                    './epp:dcp/epp:statement',
                    namespaces=NAMESPACES
                )
            ],
            'expiry': cls._extract_expiry(element.find('./epp:dcp/epp:expiry', namespaces=NAMESPACES))
        }

        return data

    @classmethod
    def _extract_statement(cls, element: Element) -> Statement:
        """Extract the statement part of Greeting.

        Args:
            element: Statement element of Greeting.

        Returns:
            Extracted Statement.
        """
        return cls.Statement(
            purpose=cls._find_children(element, './epp:purpose'),
            recipient=cls._find_children(element, './epp:recipient'),
            retention=cls._find_child(element, './epp:retention'),
        )

    @classmethod
    def _extract_expiry(cls, element: Element) -> Union[None, datetime, relativedelta]:
        """Extract the expiry part of Greeting.

        Result depends on whether the expiry is relative or absolute. Absolute expiry is returned as datetime whereas
        relative expiry is returned as timedelta.

        Args:
            element: Expiry element of Greeting.

        Returns:
            Extracted expiry expressed as either a point in time or duration until the expiry.

        Raises:
            ParsingError: If parsing of the expiry date fails.
            ValueError: If expiry is found but it does not contain "absolute" or "relative" subelement.
        """
        if element is None:
            return None

        tag = element[0].tag
        text = element[0].text

        if tag == QName(NAMESPACE.EPP, 'absolute'):
            try:
                return parse_datetime(text)
            except ValueError as exception:
                raise ParsingError('Could not parse "{}" as absolute expiry.'.format(text)) from exception
        elif tag == QName(NAMESPACE.EPP, 'relative'):
            try:
                return cls._parse_duration(text)
            except ValueError as exception:
                raise ParsingError('Could not parse "{}" as relative expiry.'.format(text)) from exception
        else:
            raise ValueError('Expected expiry specification. Found "{}" instead.'.format(tag))


class ResultData(ParseXMLMixin, ABC):
    """Base class for data obtained from epp/response/resData element."""

    @classmethod
    @abstractmethod
    def extract(cls, element: Element) -> 'ResultData':
        """Extract params for own init from the element."""


@dataclass
class Result(Response, Generic[T]):
    """EPP Result representation.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _payload_tag: ClassVar = QName(NAMESPACE.EPP, 'response')
    _res_data_class: ClassVar[Optional[Type[T]]] = None
    _res_data_path: ClassVar[Optional[str]] = None

    code: int
    message: str
    data: Sequence[T]
    cl_tr_id: str
    sv_tr_id: str

    @classmethod
    def parse(cls, raw_response: bytes, schema: XMLSchema = None) -> 'Result':
        """Parse the xml response into the Result dataclass.

        Args:
            raw_response: The raw XML response which will be parsed into the Response object.
            schema: A XML schema used to validate the parsed Response. No validation is done if schema is None.
        """
        return cast('Result', super().parse(raw_response, schema))

    @classmethod
    def _extract_payload(cls, element: Element) -> Mapping[str, Any]:
        """Extract the actual information from the response.

        Args:
            element: Child element of the epp element.
        """
        data = {
            'code': cls._optional(int, cls._find_attrib(element, './epp:result', 'code')),
            'message': cls._find_text(element, './epp:result/epp:msg'),
            'data': cls._extract_data(element.find('./epp:resData', namespaces=NAMESPACES)),
            'cl_tr_id': cls._find_text(element, './epp:trID/epp:clTRID'),
            'sv_tr_id': cls._find_text(element, './epp:trID/epp:svTRID'),
        }
        return data

    @classmethod
    def _extract_data(cls, element: Optional[Element]) -> Optional[Sequence[T]]:
        """Extract the content of the resData element.

        Args:
            element: resData epp element.
        """
        if (element is None) or (cls._res_data_path is None) or (cls._res_data_class is None):
            data = None
        else:
            data = []
            for item in element.findall(cls._res_data_path, namespaces=NAMESPACES):
                item_data = cls._res_data_class.extract(item)
                data.append(item_data)
        return data
