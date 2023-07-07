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

from unittest import TestCase

from epplib.exceptions import ParsingError


class TestParsingError(TestCase):
    def test_str(self):
        self.assertEqual(str(ParsingError()), "")
        self.assertEqual(str(ParsingError("Gazpacho!")), "Gazpacho!")
        self.assertEqual(
            str(ParsingError(raw_response="Gazpacho!")), "Raw response:\n'Gazpacho!'"
        )
