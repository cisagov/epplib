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

from difflib import unified_diff
from itertools import zip_longest
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence, Type, TypeVar, cast
from unittest import TestCase

from lxml.builder import ElementMaker
from lxml.etree import Element, QName, XMLSchema, tostring

from epplib.commands import Command, Request
from epplib.commands.command_extensions import CommandExtension
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.utils import safe_parse

T = TypeVar("T")
U = TypeVar("U")

BASE_DATA_PATH = Path(__file__).parent / "data"
SCHEMA = XMLSchema(file=str(BASE_DATA_PATH / "schemas/all-2.4.3.xsd"))

EM = ElementMaker(namespace=NAMESPACE.EPP)


def make_epp_root(*elements: Element, **kwargs: Any) -> Element:
    """Create root element of EPP so we do not have to repeat boilerplate code."""
    attrib = {QName(NAMESPACE.XSI, "schemaLocation"): SCHEMA_LOCATION.XSI}
    attrib.update(kwargs)
    return EM.epp(*elements, attrib)


def sub_dict(source: Mapping[T, U], keys: Sequence[T]) -> Mapping[T, U]:
    """Return a dictionary containing only listed keys."""
    return {k: source[k] for k in keys}


class XMLTestCase(TestCase):
    """TestCase with aditional methods for testing xml trees."""

    def assertRequestValid(
        self,
        request_class: Type[Request],
        params: Mapping[str, Any],
        extension: Optional[CommandExtension] = None,
        schema=None,
    ) -> None:
        """Assert that the generated XML complies with the schema."""
        request = request_class(**params)
        if extension is not None:
            cast(Command, request).add_extension(extension)
        xml = request.xml(tr_id="tr_id_123")
        (schema or SCHEMA).assertValid(safe_parse(xml))

    def assertXMLEqual(self, doc_1: Element, doc_2: Element) -> None:
        try:
            self._assertXMLEqual(doc_1, doc_2)
        except (
            AssertionError
        ) as error:  # pragma: no cover - Only called when the test fails.
            message = self._xml_diff(doc_1, doc_2)
            raise AssertionError("XML documents are different:\n" + message) from error

    def _assertXMLEqual(self, doc_1: Element, doc_2: Element) -> None:
        """Recursive version of assertXMLEqual where we do not catch the exceptions so we can do it at the top level."""
        self.assertEqual(doc_1.tag, doc_2.tag)
        self.assertEqual(doc_1.attrib, doc_2.attrib)
        self.assertEqual(doc_1.text, doc_2.text)
        for child_1, child_2 in zip_longest(doc_1, doc_2):
            # zip_longest returns Nones when sequence lengths differ.
            self.assertIsNotNone(child_1)
            self.assertIsNotNone(child_2)
            self._assertXMLEqual(child_1, child_2)

    def _xml_diff(
        self, doc_1: Element, doc_2: Element
    ) -> str:  # pragma: no cover - Only called when the test fails.
        """Compare str representation of XML documents and return the diff."""
        rep_1 = self._prepare_for_diff(doc_1)
        rep_2 = self._prepare_for_diff(doc_2)

        diff = unified_diff(rep_1, rep_2)
        return "".join(diff)

    def _prepare_for_diff(
        self, doc: Element
    ) -> List[str]:  # pragma: no cover - Only called when the test fails.
        """Convert Element to unified_diff input format."""
        string = cast(str, tostring(doc, pretty_print=True, encoding="unicode"))
        lines = string.splitlines(keepends=True)
        return lines
