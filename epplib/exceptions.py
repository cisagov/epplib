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

"""Module definig exceptions used in the epplib."""

from typing import Any


class EpplibException(Exception):
    """Base class for epplib Excelptions."""


class ParsingError(EpplibException):
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


class TransportError(EpplibException, RuntimeError):
    """Error to indicate problem while exchanging data with the server."""
