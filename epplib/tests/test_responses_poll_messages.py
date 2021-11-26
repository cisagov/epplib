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

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict
from unittest import TestCase

from lxml.builder import ElementMaker

from epplib.constants import NAMESPACE
from epplib.models import PostalInfo, TestResult
from epplib.models.info import InfoContactResultData, InfoDomainResultData, InfoKeysetResultData, InfoNssetResultData
from epplib.responses.poll_messages import (ContactTransfer, ContactUpdate, DelData, DnsOutageData, DomainDeletion,
                                            DomainTransfer, DomainUpdate, ExpData, IdleContactDeletion,
                                            IdleKeysetDeletion, IdleNssetDeletion, ImpendingExpData,
                                            ImpendingValExpData, KeysetTransfer, KeysetUpdate, LowCredit, NssetTransfer,
                                            NssetUpdate, RequestUsage, TechnicalCheckResult, ValExpData)


class TestPollMessages(TestCase):

    def test_low_credit(self):
        EM = ElementMaker(namespace=NAMESPACE.FRED)
        data = EM.lowCreditData(
            EM.zone('cz'),
            EM.limit(
                EM.zone('ab'),
                EM.credit('5000.00'),
            ),
            EM.credit(
                EM.zone('cd'),
                EM.credit('4999.00'),
            ),
        )
        result = LowCredit.extract(data)
        self.assertEqual(
            result,
            LowCredit(zone='cz', credit_zone='cd', credit=Decimal(4999), limit_zone='ab', limit=Decimal(5000))
        )

    def test_request_usage(self):
        EM = ElementMaker(namespace=NAMESPACE.FRED)
        data = EM.requestFeeInfoData(
            EM.periodFrom('2017-07-01T00:00:00+02:00'),
            EM.periodTo('2017-07-26T23:59:59+02:00'),
            EM.totalFreeCount('25000'),
            EM.usedCount('243'),
            EM.price('1.00'),
        )
        result = RequestUsage.extract(data)
        expected = RequestUsage(
            period_from=datetime(2017, 7, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=2))),
            period_to=datetime(2017, 7, 26, 23, 59, 59, tzinfo=timezone(timedelta(hours=2))),
            total_free_count=25000,
            used_count=243,
            price=Decimal(1),
        )
        self.assertEqual(result, expected)

    def test_domain_expiration(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        classes = (
            (ImpendingExpData, 'impendingExpData'),
            (ExpData, 'expData'),
            (DnsOutageData, 'dnsOutageData'),
            (DelData, 'delData'),
        )
        for cls, tag in classes:
            with self.subTest(tag=tag):
                data = EM(
                    tag,
                    EM.name('somedomain.cz'),
                    EM.exDate('2017-08-26'),
                )
                result = cls.extract(data)
                expected = cls(name='somedomain.cz', ex_date=date(2017, 8, 26))
                self.assertEqual(result, expected)

    def test_validation_expiration(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_ENUMVAL)
        classes = (
            (ImpendingValExpData, 'impendingValExpData'),
            (ValExpData, 'valExpData'),
        )
        for cls, tag in classes:
            with self.subTest(tag=tag):
                data = EM(
                    tag,
                    EM.name('somedomain.cz'),
                    EM.valExDate('2017-08-26'),
                )
                result = cls.extract(data)
                expected = cls(name='somedomain.cz', val_ex_date=date(2017, 8, 26))
                self.assertEqual(result, expected)

    def test_domain_transfer(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        data = EM.trnData(
            EM.name('trdomain.cz'),
            EM.trDate('2017-07-25'),
            EM.clID('REG-FRED_A'),
        )
        result = DomainTransfer.extract(data)
        expected = DomainTransfer(name='trdomain.cz', tr_date=date(2017, 7, 25), cl_id='REG-FRED_A')
        self.assertEqual(result, expected)

    def test_object_transfer(self):
        classes = (
            (ContactTransfer, NAMESPACE.NIC_CONTACT),
            (KeysetTransfer, NAMESPACE.NIC_KEYSET),
            (NssetTransfer, NAMESPACE.NIC_NSSET),
        )
        for cls, namespace in classes:
            with self.subTest(cls=cls):
                EM = ElementMaker(namespace=namespace)
                data = EM.trnData(
                    EM.id('SOME-ID'),
                    EM.trDate('2017-07-25'),
                    EM.clID('REG-FRED_A'),
                )
                result = cls.extract(data)
                expected = cls(id='SOME-ID', tr_date=date(2017, 7, 25), cl_id='REG-FRED_A')
                self.assertEqual(result, expected)

    def test_domain_update(self):
        params: Dict[str, Any] = {
            'roid': 'D0009907597',
            'cl_id': 'REG-MYREG',
            'statuses': [],
            'cr_id': None,
            'cr_date': None,
            'up_id': None,
            'up_date': None,
            'tr_date': None,
            'name': 'mydomain.cz',
            'registrant': None,
            'admins': [],
            'nsset': None,
            'keyset': None,
            'ex_date': None,
        }

        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        element = EM.updateData(
            EM.opTRID('123abc'),
            EM.oldData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.name(params['name']),
                    EM.authInfo('aaa'),
                ),
            ),
            EM.newData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.name(params['name']),
                    EM.authInfo('bbb'),
                ),
            ),
        )
        result = DomainUpdate.extract(element)
        expected = DomainUpdate(
            op_trid='123abc',
            old_data=InfoDomainResultData(auth_info='aaa', **params),
            new_data=InfoDomainResultData(auth_info='bbb', **params),
        )
        self.assertEqual(result, expected)

    def test_contact_update(self):
        params: Dict[str, Any] = {
            'roid': 'D0009907597',
            'cl_id': 'REG-MYREG',
            'statuses': [],
            'cr_id': None,
            'cr_date': None,
            'up_id': None,
            'up_date': None,
            'tr_date': None,
            'id': 'CID',
            'postal_info': PostalInfo('John', None),
            'voice': None,
            'fax': None,
            'email': None,
            'disclose': None,
            'vat': None,
            'ident': None,
            'notify_email': None,
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_CONTACT)
        element = EM.updateData(
            EM.opTRID('123abc'),
            EM.oldData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.authInfo('aaa'),
                    params['postal_info'].get_payload(),
                ),
            ),
            EM.newData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.authInfo('bbb'),
                    params['postal_info'].get_payload(),
                ),
            ),
        )
        result = ContactUpdate.extract(element)

        expected = ContactUpdate(
            op_trid='123abc',
            old_data=InfoContactResultData(auth_info='aaa', **params),
            new_data=InfoContactResultData(auth_info='bbb', **params),
        )
        self.assertEqual(result, expected)

    def test_keyset_update(self):
        params: Dict[str, Any] = {
            'roid': 'D0009907597',
            'cl_id': 'REG-MYREG',
            'statuses': [],
            'cr_id': None,
            'cr_date': None,
            'up_id': None,
            'up_date': None,
            'tr_date': None,
            'id': 'KID',
            'dnskeys': [],
            'techs': [],
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_KEYSET)
        element = EM.updateData(
            EM.opTRID('123abc'),
            EM.oldData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.authInfo('aaa'),
                ),
            ),
            EM.newData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.authInfo('bbb'),
                ),
            ),
        )
        result = KeysetUpdate.extract(element)

        expected = KeysetUpdate(
            op_trid='123abc',
            old_data=InfoKeysetResultData(auth_info='aaa', **params),
            new_data=InfoKeysetResultData(auth_info='bbb', **params),
        )
        self.assertEqual(result, expected)

    def test_nsset_update(self):
        params: Dict[str, Any] = {
            'roid': 'D0009907597',
            'cl_id': 'REG-MYREG',
            'statuses': [],
            'cr_id': None,
            'cr_date': None,
            'up_id': None,
            'up_date': None,
            'tr_date': None,
            'id': 'NID',
            'nss': [],
            'techs': [],
            'report_level': 4,
        }
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        element = EM.updateData(
            EM.opTRID('123abc'),
            EM.oldData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.reportlevel(str(params['report_level'])),
                    EM.authInfo('aaa'),
                ),
            ),
            EM.newData(
                EM.infData(
                    EM.roid('D0009907597'),
                    EM.clID('REG-MYREG'),
                    EM.id(params['id']),
                    EM.reportlevel(str(params['report_level'])),
                    EM.authInfo('bbb'),
                ),
            ),
        )
        result = NssetUpdate.extract(element)

        expected = NssetUpdate(
            op_trid='123abc',
            old_data=InfoNssetResultData(auth_info='aaa', **params),
            new_data=InfoNssetResultData(auth_info='bbb', **params),
        )
        self.assertEqual(result, expected)

    def test_idle_object_deletion(self):
        classes = (
            (IdleContactDeletion, NAMESPACE.NIC_CONTACT),
            (IdleKeysetDeletion, NAMESPACE.NIC_KEYSET),
            (IdleNssetDeletion, NAMESPACE.NIC_NSSET),
        )
        for cls, namespace in classes:
            with self.subTest(cls=cls):
                EM = ElementMaker(namespace=namespace)
                data = EM.idleDelData(
                    EM.id('SOME-ID'),
                )
                result = cls.extract(data)
                expected = cls(id='SOME-ID')
                self.assertEqual(result, expected)

    def test_domain_deletion(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_DOMAIN)
        data = EM.delData(
            EM.name('example.cz'),
            EM.exDate('2019-07-30'),
        )
        result = DomainDeletion.extract(data)
        expected = DomainDeletion(name='example.cz', ex_date=date(2019, 7, 30))
        self.assertEqual(result, expected)

    def test_technical_check_result(self):
        EM = ElementMaker(namespace=NAMESPACE.NIC_NSSET)
        data = EM.testData(
            EM.id('NID-MYNSSET'),
            EM.name('example.cz'),
            EM.result(
                EM.testname('glue_ok'),
                EM.status('true'),
            ),
            EM.result(
                EM.testname('existence'),
                EM.status('false'),
            )
        )
        result = TechnicalCheckResult.extract(data)
        expected = TechnicalCheckResult(
            id='NID-MYNSSET',
            names=['example.cz'],
            results=[
                TestResult('glue_ok', True, None),
                TestResult('existence', False, None),
            ]
        )
        self.assertEqual(result, expected)
