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

"""Module providing EPP commands."""

from .base import Command, Hello, Login, Logout, Request
from .check import CheckContact, CheckDomain, CheckHost, CheckKeyset, CheckNsset
from .create import CreateContact, CreateDomain, CreateHost, CreateKeyset, CreateNsset
from .delete import DeleteContact, DeleteDomain, DeleteHost, DeleteKeyset, DeleteNsset
from .extensions import (
    CreditInfoRequest,
    SendAuthInfoContact,
    SendAuthInfoDomain,
    SendAuthInfoKeyset,
    SendAuthInfoNsset,
    TestNsset,
)
from .info import InfoContact, InfoDomain, InfoHost, InfoKeyset, InfoNsset
from .list import (
    ListContacts,
    ListDomains,
    ListDomainsByContact,
    ListDomainsByKeyset,
    ListDomainsByNsset,
    ListKeysets,
    ListKeysetsByContact,
    ListNssets,
    ListNssetsByContact,
    ListNssetsByNs,
    ListResult,
)
from .renew import RenewDomain
from .transfer import TransferContact, TransferDomain, TransferKeyset, TransferNsset
from .update import UpdateContact, UpdateDomain, UpdateHost, UpdateKeyset, UpdateNsset

__all__ = [
    "CheckContact",
    "CheckDomain",
    "CheckHost",
    "CheckKeyset",
    "CheckNsset",
    "Command",
    "CreateContact",
    "CreateDomain",
    "CreateHost",
    "CreateKeyset",
    "CreateNsset",
    "CreditInfoRequest",
    "DeleteContact",
    "DeleteDomain",
    "DeleteHost",
    "DeleteKeyset",
    "DeleteNsset",
    "Hello",
    "InfoContact",
    "InfoDomain",
    "InfoHost",
    "InfoKeyset",
    "InfoNsset",
    "ListContacts",
    "ListDomains",
    "ListDomainsByContact",
    "ListDomainsByKeyset",
    "ListDomainsByNsset",
    "ListKeysets",
    "ListKeysetsByContact",
    "ListNssets",
    "ListNssetsByContact",
    "ListNssetsByNs",
    "ListResult",
    "Login",
    "Logout",
    "RenewDomain",
    "Request",
    "SendAuthInfoContact",
    "SendAuthInfoDomain",
    "SendAuthInfoKeyset",
    "SendAuthInfoNsset",
    "TestNsset",
    "TransferContact",
    "TransferDomain",
    "TransferKeyset",
    "TransferNsset",
    "UpdateContact",
    "UpdateDomain",
    "UpdateHost",
    "UpdateKeyset",
    "UpdateNsset",
]
