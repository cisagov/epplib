from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase

from epplib.models import Status
from epplib.models.common import DomainAuthInfo, DomainContact
from epplib.models.info import InfoDomainResultData
from epplib.responses import InfoDomainResult
from dateutil.tz import tzutc
from unittest.mock import patch 
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
@patch("epplib.models.common.NAMESPACE", NAMESPACE)
@patch("epplib.responses.base.NAMESPACE", NAMESPACE)
@patch("epplib.utils.NAMESPACE", NAMESPACE)
@patch("epplib.constants", NAMESPACE)
@patch("epplib.constants", SCHEMA_LOCATION)
@patch(
    "epplib.utils.ParseXMLMixin._NAMESPACES", 
    {
    "epp": NAMESPACE.EPP,
    "fred": NAMESPACE.FRED,
    "secDNS": NAMESPACE.SEC_DNS,
    "contact": NAMESPACE.NIC_CONTACT,
    "domain": NAMESPACE.NIC_DOMAIN,
    "host": NAMESPACE.NIC_HOST,
    "keyset": NAMESPACE.NIC_KEYSET,
    "nsset": NAMESPACE.NIC_NSSET,
    }
)
class TestInfoDomainResult(TestCase):
    
    def test_parse_minimal(self):
        location= Path(__file__).parent / "data" / "infoDomain.xml"
        xml = (location).read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResultData(
                name="test3.gov",
                roid="DF1340360-GOV",
                statuses=[Status("serverTransferProhibited", None, None),Status("inactive", None, None)],
                cl_id="gov2023-ote",
                contacts=[DomainContact(contact='CONT2', type='security'), DomainContact(contact='CONT3', type='tech'),],
                registrant="TuaWnx9hnm84GCSU",
                admins=[],
                nsset=None,
                keyset=None,
                cr_id="gov2023-ote",
                cr_date=datetime(2023, 8, 15, 23, 56, 36, tzinfo=tzutc()),
                up_id="gov2023-ote",
                up_date=datetime(2023, 8, 17, 2, 3, 19, tzinfo=tzutc()),
                ex_date=date(2024, 8, 15),
                tr_date=None,
                auth_info=DomainAuthInfo(pw="2fooBAR123fooBaz")
            )
        ]
        text_to_check = "DomainContact(contact='CONT2', type='security')"

        # The right code is returned
        self.assertEqual(result.code, 1000)

        # Both objects are the same       
        self.assertEqual(result.res_data, expected)

        # Both objects have the same contacts
        self.assertEqual(result.res_data[0].contacts, expected[0].contacts)

        # Manually checks for contacts on the returned object (Tests for optional vars)
        self.assertIn(text_to_check, str(result.res_data[0]))

        text_to_check = "DomainContact(contact='CONT3', type='tech')"
        self.assertIn(text_to_check, str(result.res_data[0]))

    def test_parse_minimal_no_contact(self):
        location= Path(__file__).parent / "data" / "infoDomainNoContact.xml"
        text_to_check = "contacts=[]"
        xml = (location).read_bytes()
        result = InfoDomainResult.parse(xml, SCHEMA)
        expected = [
            InfoDomainResultData(
                name="test3.gov",
                roid="DF1340360-GOV",
                statuses=[Status("serverTransferProhibited", None, None),Status("inactive", None, None)],
                cl_id="gov2023-ote",
                registrant="TuaWnx9hnm84GCSU",
                admins=[],
                nsset=None,
                keyset=None,
                cr_id="gov2023-ote",
                cr_date=datetime(2023, 8, 15, 23, 56, 36, tzinfo=tzutc()),
                up_id="gov2023-ote",
                up_date=datetime(2023, 8, 17, 2, 3, 19, tzinfo=tzutc()),
                ex_date=date(2024, 8, 15),
                tr_date=None,
                auth_info=DomainAuthInfo(pw="2fooBAR123fooBaz")
            )
        ]

        # The right code is returned
        self.assertEqual(result.code, 1000)

        # Both objects are the same        
        self.assertEqual(result.res_data, expected)

        # Both objects have the same contacts
        self.assertEqual(result.res_data[0].contacts, expected[0].contacts)

        # Manually checks for contacts on the returned object (Tests for optional vars)
        self.assertIn(text_to_check, str(result.res_data[0]))

