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

"""Module providing various utility functions."""

from lxml.etree import Element, XMLParser, fromstring


def safe_parse(raw_xml: bytes) -> Element:
    """Wrap lxml.etree.fromstring function to make it safer against XML attacks.

    Args:
        raw_xml: The raw XML response which will be parsed.
    """
    parser = XMLParser(no_network=True, resolve_entities=False)
    parsed = fromstring(raw_xml, parser=parser)  # nosec - It should be safe with resolve_entities=False.

    if parsed.getroottree().docinfo.doctype:
        raise ValueError('Doctype is not allowed.')

    return parsed
