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
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Generic, List, Mapping, Optional, Sequence, Type, TypeVar, Union, cast

from dateutil.parser import parse as parse_datetime
from dateutil.relativedelta import relativedelta
from lxml.etree import Element, QName, XMLSchema

from epplib.constants import NAMESPACE
from epplib.exceptions import ParsingError
from epplib.responses.extensions import EnumInfoExtension, ResponseExtension
from epplib.utils import ParseXMLMixin, safe_parse

EXTENSIONS: Dict[QName, Type[ResponseExtension]] = {EnumInfoExtension.tag: EnumInfoExtension}
LOGGER = logging.getLogger(__name__)

T = TypeVar('T', bound='ResultData')

GreetingPayload = Mapping[str, Union[None, Sequence[str], Sequence['Greeting.Statement'], datetime, relativedelta, str]]


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
                    namespaces=cls._NAMESPACES
                )
            ],
            'expiry': cls._extract_expiry(element.find('./epp:dcp/epp:expiry', namespaces=cls._NAMESPACES))
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
        extensions: Content of the epp/response/extension element.
    """

    _payload_tag: ClassVar = QName(NAMESPACE.EPP, 'response')
    _res_data_class: ClassVar[Optional[Type[T]]] = None
    _res_data_path: ClassVar[Optional[str]] = None

    code: int
    message: str
    data: Sequence[T]
    cl_tr_id: str
    sv_tr_id: str
    extensions: Sequence[ResponseExtension] = field(default_factory=list)

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
        payload_data = {
            'code': cls._optional(int, cls._find_attrib(element, './epp:result', 'code')),
            'message': cls._find_text(element, './epp:result/epp:msg'),
            'data': cls._extract_data(cls._find(element, './epp:resData')),
            'cl_tr_id': cls._find_text(element, './epp:trID/epp:clTRID'),
            'sv_tr_id': cls._find_text(element, './epp:trID/epp:svTRID'),
            'extensions': cls._extract_extensions(cls._find(element, './epp:extension')),
        }
        return payload_data

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
            for item in element.findall(cls._res_data_path, namespaces=cls._NAMESPACES):
                item_data = cls._res_data_class.extract(item)
                data.append(item_data)
        return data

    @classmethod
    def _extract_extensions(cls, element: Optional[Element]) -> Sequence[ResponseExtension]:
        data = []
        if element is not None:
            for child in element:
                extension_class = EXTENSIONS.get(child.tag, None)
                if extension_class is None:
                    LOGGER.info('Could not find class to extract extension {}.'.format(child.tag))
                else:
                    data.append(extension_class.extract(child))
        return data
