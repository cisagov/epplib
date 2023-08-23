from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase

from epplib.models import Status
from epplib.models.common import DomainAuthInfo
from epplib.models.info import InfoDomainResultData
from epplib.responses import InfoDomainResult

from unittest.mock import patch 
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
@patch("epplib.commands.info.NAMESPACE", NAMESPACE)
@patch("epplib.commands.info.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.DomainAuthInfo.namespace", NAMESPACE.NIC_DOMAIN)
class TestInfoDomainResult(TestCase):
    def test_parse_minimal(self):
        location= Path(__file__).parent / "data" / "infoDomain.xml"
        print(location)
        xml = (location).read_bytes()
        print(xml)
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResultData(
                name="test3.gov",
                roid="DF1340360-GOV",
                statuses=[Status("serverTransferProhibited", "", None),Status("inactive", "", None)],
                cl_id="gov2023-ote",
                contacts=["CONT2","CONT3"],
                registrant="TuaWnx9hnm84GCSU",
                admins=[],
                nsset=None,
                keyset=None,
                cr_id="gov2023-ote",
                cr_date="2023-08-15T23:56:36Z",
                up_id=None,
                up_date="2023-08-17T02:03:19Z",
                ex_date="2024-08-15T23:56:36Z",
                tr_date=None,
                auth_info=DomainAuthInfo(pw="2fooBAR123fooBaz"),
            )
        ]
        print(result)
        self.assertEqual(result.code, 1000)
        print("result.res_data")
        print(result.res_data)        
        self.assertEqual(result.res_data, expected)

    # def test_parse_full(self):
    #     xml = (path(__file__).parent  / "responses/result_info_domain.xml").read_bytes()
    #     result = InfoDomainResult.parse(xml, SCHEMA)
    #     expected = [
    #         InfoDomainResultData(
    #             name="mydomain.cz",
    #             roid="D0009907597-CZ",
    #             statuses=[Status("ok", "Object is without restrictions", "en")],
    #             cl_id="REG-MYREG",
    #             registrant="CID-MYOWN",
    #             admins=["CID-ADMIN2", "CID-ADMIN3"],
    #             nsset="NID-MYNSSET",
    #             keyset="KID-MYKEYSET",
    #             cr_id="REG-MYREG",
    #             cr_date=datetime(
    #                 2017, 7, 11, 13, 28, 48, tzinfo=timezone(timedelta(hours=2))
    #             ),
    #             up_id="REG-MYREG",
    #             up_date=datetime(
    #                 2017, 7, 18, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))
    #             ),
    #             ex_date=date(2020, 7, 11),
    #             tr_date=datetime(
    #                 2017, 7, 19, 10, 46, 19, tzinfo=timezone(timedelta(hours=2))
    #             ),
    #             auth_info="rvBcaTVq",
    #         )
    #     ]

    #     self.assertEqual(result.code, 1000)
    #     self.assertEqual(result.res_data, expected)

    # def test_parse_error(self):
    #     xml = (BASE_DATA_PATH / "responses/result_error.xml").read_bytes()
    #     result = InfoDomainResult.parse(xml, SCHEMA)
    #     self.assertEqual(result.code, 2002)

