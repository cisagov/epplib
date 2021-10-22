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

from dataclasses import dataclass
from typing import Any, Dict

from lxml.etree import Element, QName, fromstring

from epplib.commands.extensions import Extension
from epplib.responses import Response
from epplib.tests.utils import EM, XMLTestCase, make_epp_root

EXTENSION_NAMESPACE = 'extension:name:space'


class DummyResponse(Response):
    @classmethod
    def _parse_payload(csl, element) -> Dict[str, Any]:
        return dict()  # pragma: no cover


@dataclass
class DummyExtension(Extension):
    response_class = DummyResponse

    def _get_extension_payload(self) -> Element:
        return Element(QName(EXTENSION_NAMESPACE, 'dummy'))


class TestExtension(XMLTestCase):
    def test_extension(self):
        root = fromstring(DummyExtension().xml())
        expected = make_epp_root(
            EM.extension(
                EM(str(QName(EXTENSION_NAMESPACE, 'dummy'))),
            )
        )
        self.assertXMLEqual(root, expected)
