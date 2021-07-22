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

"""A transport layer to support the Epp client."""
from abc import ABC, abstractmethod
from os import PathLike
from typing import Union

PathType = Union[str, PathLike]


class Transport(ABC):
    """Abstract base class for Transport."""

    @abstractmethod
    def connect(self) -> None:
        """Open the connection to the EPP server."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection gracefully."""

    @abstractmethod
    def send(self, message: bytes) -> None:
        """Send data to the server."""

    @abstractmethod
    def receive(self) -> bytes:
        """Receive data from the server."""
