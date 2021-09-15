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
from typing import Any, ClassVar, Generic, List, Mapping, Optional, Sequence, Type, TypeVar, Union, cast

from isodate import Duration, parse_datetime, parse_duration
from isodate.isoerror import ISO8601Error
from lxml.etree import Element, QName, XMLSchema

from epplib.constants import NAMESPACE_EPP, NAMESPACE_NIC_CONTACT, NAMESPACE_NIC_DOMAIN, NAMESPACE_NIC_NSSET
from epplib.utils import safe_parse

NAMESPACES = {
    'epp': NAMESPACE_EPP,
    'contact': NAMESPACE_NIC_CONTACT,
    'domain': NAMESPACE_NIC_DOMAIN,
    'nsset': NAMESPACE_NIC_NSSET,
}

GreetingPayload = Mapping[str, Union[None, Sequence[str], Sequence['Greeting.Statement'], datetime, str, timedelta]]

T = TypeVar('T', bound='ResultData')


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
    def _optional_int(value: Optional[str]) -> Optional[int]:
        if value is None:
            return None
        else:
            return int(value)

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

        if root.tag != QName(NAMESPACE_EPP, 'epp'):
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

    _payload_tag: ClassVar = QName(NAMESPACE_EPP, 'greeting')

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
    def _extract_expiry(cls, element: Element) -> Union[None, datetime, timedelta]:
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

        if tag == QName(NAMESPACE_EPP, 'absolute'):
            try:
                return parse_datetime(text)
            except (ISO8601Error, ValueError) as exception:
                raise ParsingError('Could not parse "{}" as absolute expiry.'.format(text)) from exception
        elif tag == QName(NAMESPACE_EPP, 'relative'):
            try:
                result = parse_duration(text)
            except (ISO8601Error, ValueError) as exception:
                raise ParsingError('Could not parse "{}" as relative expiry.'.format(text)) from exception
            if isinstance(result, Duration):
                result = result.totimedelta(datetime.now())
            return result
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

    _payload_tag: ClassVar = QName(NAMESPACE_EPP, 'response')
    _res_data_class: ClassVar[Type[T]]

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
    def _extract_payload(cls, element: Element) -> Mapping[str, Union[None, int, str, Sequence[Any]]]:
        """Extract the actual information from the response.

        Args:
            element: Child element of the epp element.
        """
        data = {
            'code': cls._optional_int(cls._find_attrib(element, './epp:result', 'code')),
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
        return None


class CheckResult(Result[T]):
    """Represents EPP Result which responds to the Check command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    _res_data_path: ClassVar[str]

    @classmethod
    def _extract_data(cls, element: Optional[Element]) -> Sequence[T]:
        """Extract the content of the resData element.

        Args:
            element: resData epp element.
        """
        data = []
        if element is not None:
            for item in element.findall(cls._res_data_path, namespaces=NAMESPACES):
                item_data = cls._res_data_class.extract(item)
                data.append(item_data)
        return data


@dataclass
class CheckDomainResult(CheckResult):
    """Represents EPP Result which responds to the Check domain command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Domain(ResultData):
        """Dataclass representing domain availability in the check domain result.

        Attributes:
            name: Content of the epp/response/resData/chkData/cd/name element.
            available: Avail attribute of the epp/response/resData/chkData/cd/name element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        name: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckDomainResult.Domain':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './domain:name'),
                cls._str_to_bool(cls._find_attrib(element, './domain:name', 'avail')),
                cls._find_text(element, './domain:reason'),
            )
            return cls(*params)

    _res_data_path: ClassVar[str] = './domain:chkData/domain:cd'
    _res_data_class: ClassVar = Domain


@dataclass
class CheckContactResult(CheckResult):
    """Represents EPP Result which responds to the Check contact command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Contact(ResultData):
        """Dataclass representing contact availability in the check contact result.

        Attributes:
            id: Content of the epp/response/resData/chkData/cd/id element.
            available: Avail attribute of the epp/response/resData/chkData/cd/id element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        id: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckContactResult.Contact':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './contact:id'),
                cls._str_to_bool(cls._find_attrib(element, './contact:id', 'avail')),
                cls._find_text(element, './contact:reason'),
            )
            return cls(*params)

    _res_data_path = './contact:chkData/contact:cd'
    _res_data_class: ClassVar = Contact


@dataclass
class CheckNssetResult(CheckResult):
    """Represents EPP Result which responds to the Check nsset command.

    Attributes:
        code: Code attribute of the epp/response/result element.
        message: Content of the epp/response/result/msg element.
        data: Content of the epp/response/result/resData element.
        cl_tr_id: Content of the epp/response/trID/clTRID element.
        sv_tr_id: Content of the epp/response/trID/svTRID element.
    """

    @dataclass
    class Nsset(ResultData):
        """Dataclass representing nsset availability in the check nsset result.

        Attributes:
            id: Content of the epp/response/resData/chkData/cd/id element.
            available: Avail attribute of the epp/response/resData/chkData/cd/id element.
            reason: Content of the epp/response/resData/chkData/cd/reason element.
        """

        id: str
        available: Optional[bool]
        reason: Optional[str] = None

        @classmethod
        def extract(cls, element: Element) -> 'CheckNssetResult.Nsset':
            """Extract params for own init from the element."""
            params = (
                cls._find_text(element, './nsset:id'),
                cls._str_to_bool(cls._find_attrib(element, './nsset:id', 'avail')),
                cls._find_text(element, './nsset:reason'),
            )
            return cls(*params)

    _res_data_path = './nsset:chkData/nsset:cd'
    _res_data_class: ClassVar = Nsset
