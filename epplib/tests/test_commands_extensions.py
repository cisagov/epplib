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
from typing import Any, Dict, Mapping

from lxml.builder import ElementMaker
from lxml.etree import Element, QName, fromstring

from epplib.commands import CreditInfoRequest, SendAuthInfoDomain, SendAuthInfoKeyset, TestNsset
from epplib.commands.extensions import Extension
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.responses import Response
from epplib.tests.utils import EM, XMLTestCase, make_epp_root, sub_dict

EXTENSION_NAMESPACE = 'extension:name:space'
tr_id = 'abc123'


class DummyResponse(Response):
    @classmethod
    def _parse_payload(csl, element) -> Dict[str, Any]:
        return dict()  # pragma: no cover


@dataclass
class DummyExtension(Extension):
    response_class = DummyResponse

    def _get_extension_payload(self, tr_id: str = None) -> Element:
        root = Element(QName(EXTENSION_NAMESPACE, 'dummy'))
        if tr_id is not None:
            root.text = tr_id
        return root


class TestExtension(XMLTestCase):

    def test_extension(self):
        root = fromstring(DummyExtension().xml())
        expected = make_epp_root(
            EM.extension(
                EM(str(QName(EXTENSION_NAMESPACE, 'dummy'))),
            )
        )
        self.assertXMLEqual(root, expected)

    def test_extension_tr_id(self):
        tr_id = 'abc123'
        root = fromstring(DummyExtension().xml(tr_id))
        expected = make_epp_root(
            EM.extension(
                EM(str(QName(EXTENSION_NAMESPACE, 'dummy')), tr_id),
            )
        )
        self.assertXMLEqual(root, expected)


class TestCreditInfo(XMLTestCase):

    def test_valid(self):
        self.assertRequestValid(CreditInfoRequest, {})

    def test_data(self):
        root = fromstring(CreditInfoRequest().xml(tr_id))
        fred = ElementMaker(namespace=NAMESPACE.FRED)
        expected = make_epp_root(
            EM.extension(
                fred.extcommand(
                    {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                    fred.creditInfo(),
                    fred.clTRID(tr_id)
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestSendAuthInfoDomain(XMLTestCase):

    domain = 'mydomain.cz'

    def test_valid(self):
        self.assertRequestValid(SendAuthInfoDomain, {'name': self.domain})

    def test_data(self):
        root = fromstring(SendAuthInfoDomain(name=self.domain).xml(tr_id))
        fred = ElementMaker(namespace=NAMESPACE.FRED)
        domain = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        expected = make_epp_root(
            EM.extension(
                fred.extcommand(
                    {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                    fred.sendAuthInfo(
                        domain.sendAuthInfo(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_DOMAIN},
                            domain.name(self.domain),
                        ),
                    ),
                    fred.clTRID(tr_id),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestSendAuthInfoKeyset(XMLTestCase):

    keyset = 'KID-MYKEYSET'

    def test_valid(self):
        self.assertRequestValid(SendAuthInfoKeyset, {'id': self.keyset})

    def test_data(self):
        root = fromstring(SendAuthInfoKeyset(id=self.keyset).xml(tr_id))
        fred = ElementMaker(namespace=NAMESPACE.FRED)
        keyset = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        expected = make_epp_root(
            EM.extension(
                fred.extcommand(
                    {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                    fred.sendAuthInfo(
                        keyset.sendAuthInfo(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_KEYSET},
                            keyset.id(self.keyset),
                        ),
                    ),
                    fred.clTRID(tr_id),
                ),
            )
        )
        self.assertXMLEqual(root, expected)


class TestTestNsset(XMLTestCase):

    params: Mapping[str, Any] = {
        'id': 'NID-MYNSSET',
        'level': 5,
        'names': ['mydomain.cz', 'somedomain.cz']
    }
    required = ['id']

    def test_valid(self):
        self.assertRequestValid(TestNsset, self.params)
        self.assertRequestValid(TestNsset, sub_dict(self.params, self.required))

    def test_data_minimal(self):
        root = fromstring(TestNsset(**sub_dict(self.params, self.required)).xml(tr_id))
        fred = ElementMaker(namespace=NAMESPACE.FRED)
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.extension(
                fred.extcommand(
                    {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                    fred.test(
                        nsset.test(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_NSSET},
                            nsset.id(self.params['id']),
                        ),
                    ),
                    fred.clTRID(tr_id),
                ),
            ),
        )
        self.assertXMLEqual(root, expected)

    def test_data_full(self):
        root = fromstring(TestNsset(**self.params).xml(tr_id))
        fred = ElementMaker(namespace=NAMESPACE.FRED)
        nsset = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        expected = make_epp_root(
            EM.extension(
                fred.extcommand(
                    {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.FRED},
                    fred.test(
                        nsset.test(
                            {QName(NAMESPACE.XSI, 'schemaLocation'): SCHEMA_LOCATION.NIC_NSSET},
                            nsset.id(self.params['id']),
                            nsset.level(str(self.params['level'])),
                            nsset.name(self.params['names'][0]),
                            nsset.name(self.params['names'][1]),
                        ),
                    ),
                    fred.clTRID(tr_id),
                ),
            ),
        )
        self.assertXMLEqual(root, expected)
