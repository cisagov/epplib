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

from itertools import zip_longest
from pathlib import Path
from typing import Any, Dict, Type
from unittest import TestCase

from lxml.builder import ElementMaker
from lxml.etree import Element, QName, XMLSchema

from epplib.commands import Request
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.utils import safe_parse

BASE_DATA_PATH = Path(__file__).parent / 'data'
SCHEMA = XMLSchema(file=str(BASE_DATA_PATH / 'schemas/all-2.4.1.xsd'))

EM = ElementMaker(namespace=NAMESPACE.EPP)


def make_epp_root(*elements, **kwargs) -> Element:
    """Create root element of EPP so we do not have to repeat boilerplate code."""
    attrib = {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.XSI}
    attrib.update(kwargs)
    return EM.epp(*elements, attrib)


class XMLTestCase(TestCase):
    """TestCase with aditional methods for testing xml trees."""

    def assertRequestValid(self, request_class: Type[Request], params: Dict[str, Any]):
        """Assert that the generated XML complies with the schema."""
        request = request_class(**params)  # type: ignore
        xml = request.xml(tr_id='tr_id_123')
        SCHEMA.assertValid(safe_parse(xml))

    def assertXMLEqual(self, doc_1: Element, doc_2: Element) -> None:
        self.assertEqual(doc_1.tag, doc_2.tag)
        self.assertEqual(doc_1.attrib, doc_2.attrib)
        self.assertEqual(doc_1.text, doc_2.text)
        for child_1, child_2 in zip_longest(doc_1, doc_2):
            self.assertXMLEqual(child_1, child_2)
