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

"""Module providing various utility functions."""

import re
from datetime import date
from typing import Callable, ClassVar, List, Mapping, Optional, Pattern, TypeVar, cast

from dateutil.parser import parse as parse_datetime
from dateutil.relativedelta import relativedelta
from lxml.etree import Element, QName, XMLParser, fromstring

from epplib.constants import NAMESPACE

U = TypeVar('U')


def safe_parse(raw_xml: bytes) -> Element:
    """Wrap lxml.etree.fromstring function to make it safer against XML attacks.

    Args:
        raw_xml: The raw XML response which will be parsed.

    Raises:
        ValueError: If the XML document contains doctype.
    """
    parser = XMLParser(no_network=True, resolve_entities=False)
    parsed = fromstring(raw_xml, parser=parser)  # nosec - It should be safe with resolve_entities=False.

    if parsed.getroottree().docinfo.doctype:
        raise ValueError('Doctype is not allowed.')

    return parsed


class ParseXMLMixin:
    """Mixin to simplify XML parsing."""

    _NAMESPACES: ClassVar[Mapping[str, str]] = {
        'epp': NAMESPACE.EPP,
        'fred': NAMESPACE.FRED,
        'secDNS':NAMESPACE.SEC_DNS,
        'contact': NAMESPACE.NIC_CONTACT,
        'domain': NAMESPACE.NIC_DOMAIN,
        'host': NAMESPACE.NIC_HOST,
        'keyset': NAMESPACE.NIC_KEYSET,
        'nsset': NAMESPACE.NIC_NSSET
    }
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

    @classmethod
    def _find(cls, element: Element, path: str) -> Optional[Element]:
        return element.find(path, namespaces=cls._NAMESPACES)

    @classmethod
    def _find_all(cls, element: Element, path: str) -> List[Element]:
        return cast(List[Element], element.findall(path, namespaces=cls._NAMESPACES))

    @classmethod
    def _find_text(cls, element: Element, path: str) -> str:
        return cast(str, element.findtext(path, namespaces=cls._NAMESPACES))

    @classmethod
    def _find_all_text(cls, element: Element, path: str) -> List[str]:
        return [(elem.text or '') for elem in element.findall(path, namespaces=cls._NAMESPACES)]

    @classmethod
    def _find_attrib(cls, element: Element, path: str, attrib: str) -> Optional[str]:
        found = element.find(path, namespaces=cls._NAMESPACES)
        if found is not None:
            return cast(Optional[str], found.attrib.get(attrib))
        else:
            return None

    @classmethod
    def _find_child(cls, element: Element, path: str) -> Optional[str]:
        found_tags = cls._find_children(element, path)
        if len(found_tags) > 0:
            return found_tags[0]
        else:
            return None

    @classmethod
    def _find_children(cls, element: Element, path: str) -> List[str]:
        nodes = element.findall(path + '/*', namespaces=cls._NAMESPACES)
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
        elif value.lower() in ('1', 'true'):
            return True
        elif value.lower() in ('0', 'false'):
            return False
        else:
            raise ValueError('Value "{}" is not in the list of known boolean values.'.format(value))
