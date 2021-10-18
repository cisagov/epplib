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

from epplib.models import Status
from epplib.tests.utils import XMLTestCase


class TestStatus(XMLTestCase):

    def test_post_init(self):
        self.assertEqual(Status('ok', 'is ok', 'cs'), Status('ok', 'is ok', 'cs'))
        self.assertEqual(Status('ok', 'is ok'), Status('ok', 'is ok', 'en'))
        self.assertEqual(Status('ok', 'is ok', None), Status('ok', 'is ok', 'en'))
