from typing import Any, Dict, Mapping, cast
from unittest.mock import patch
from lxml.builder import ElementMaker
from lxml import etree

from epplib.commands import CreateDomain
from epplib.commands.command_extensions import (
    CreateDomainDNSSECExtension,
    UpdateDomainDNSSECExtension,
)

from epplib.commands.update import UpdateDomain
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import EM, XMLTestCase, make_epp_root
from epplib.models.common import DSData, DomainAuthInfo, DNSSECKeyData
from unittest import TestCase
from epplib.responses.extensions import DNSSECExtension


keyDataDict = {"flags": 257, "protocol": 3, "alg": 1, "pubKey": "AQPJ////4Q=="}
keyDataDict2 = {"flags": 267, "protocol": 1, "alg": 3, "pubKey": "AQPJ////4Q=="}
dsDataDict = {
    "keyTag": 12345,
    "alg": 3,
    "digestType": 1,
    "digest": "49FD46E6C4B45C55D4AC",
    "keyData": DNSSECKeyData(**keyDataDict),
}
dsDataIncomplete = {
    "keyTag": 1234,
    "alg": 2,
    "digestType": 0,
    "digest": "49FD46E6C4B45C55D4AC",
}

paramsWithDsData: Mapping[str, Any] = {
    "maxSigLife": 3215,
    "dsData": [DSData(**dsDataDict)],
}

paramsWithKeyData: Mapping[str, Any] = {
    "maxSigLife": 3215,
    "keyData": [DNSSECKeyData(**keyDataDict)],
}
paramsWithMultiKeyData: Mapping[str, Any] = {
    "maxSigLife": 3215,
    "keyData": [DNSSECKeyData(**keyDataDict), DNSSECKeyData(**keyDataDict2)],
}
paramsWithMultiDsData: Mapping[str, Any] = {
    "maxSigLife": 3215,
    "dsData": [DSData(**dsDataDict), DSData(**dsDataIncomplete)],
}

command_params: Dict[str, Any] = {
    "name": "thisdomain.cz",
    "registrant": "CID-MYOWN",
    "auth_info": DomainAuthInfo(pw="2fooBAR123fooBaz"),
}


@patch("epplib.commands.create.NAMESPACE", NAMESPACE)
@patch("epplib.commands.create.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.DomainAuthInfo.namespace", NAMESPACE.NIC_DOMAIN)
@patch("epplib.constants", NAMESPACE)
@patch("epplib.constants.SCHEMA_LOCATION", SCHEMA_LOCATION)
class TestCreateDomainDNSSecExtension(XMLTestCase):
    def test_data_with_dsData(self):
        extension = CreateDomainDNSSECExtension(**paramsWithMultiDsData)
        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )

        expected = EM.create(
            EM.maxSigLife(str(paramsWithMultiDsData["maxSigLife"])),
            EM.dsData(
                EM.keyTag(str(dsDataDict["keyTag"])),
                EM.alg(str(dsDataDict["alg"])),
                EM.digestType(str(dsDataDict["digestType"])),
                EM.digest(dsDataDict["digest"]),
                EM.keyData(
                    EM.flags(str(keyDataDict["flags"])),
                    EM.protocol(str(keyDataDict["protocol"])),
                    EM.alg(str(keyDataDict["alg"])),
                    EM.pubKey(str(keyDataDict["pubKey"])),
                ),
            ),
            EM.dsData(
                EM.keyTag(str(dsDataIncomplete["keyTag"])),
                EM.alg(str(dsDataIncomplete["alg"])),
                EM.digestType(str(dsDataIncomplete["digestType"])),
                EM.digest(dsDataIncomplete["digest"]),
            ),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_data_with_keyData(self):
        extension = CreateDomainDNSSECExtension(**paramsWithKeyData)

        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )
        expected = EM.create(
            EM.maxSigLife(str(paramsWithKeyData["maxSigLife"])),
            EM.keyData(
                EM.flags(str(keyDataDict["flags"])),
                EM.protocol(str(keyDataDict["protocol"])),
                EM.alg(str(keyDataDict["alg"])),
                EM.pubKey(str(keyDataDict["pubKey"])),
            ),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_data_with_multi_keyData(self):
        extension = CreateDomainDNSSECExtension(**paramsWithMultiKeyData)

        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )
        expected = EM.create(
            EM.maxSigLife(str(paramsWithKeyData["maxSigLife"])),
            EM.keyData(
                EM.flags(str(keyDataDict["flags"])),
                EM.protocol(str(keyDataDict["protocol"])),
                EM.alg(str(keyDataDict["alg"])),
                EM.pubKey(str(keyDataDict["pubKey"])),
            ),
            EM.keyData(
                EM.flags(str(keyDataDict2["flags"])),
                EM.protocol(str(keyDataDict2["protocol"])),
                EM.alg(str(keyDataDict2["alg"])),
                EM.pubKey(str(keyDataDict2["pubKey"])),
            ),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_valid(self):
        extension = CreateDomainDNSSECExtension(**paramsWithMultiDsData)
        self.assertRequestValid(
            CreateDomain, command_params, extension=extension, schema=SCHEMA
        )


@patch("epplib.commands.update.NAMESPACE", NAMESPACE)
@patch("epplib.commands.update.SCHEMA_LOCATION", SCHEMA_LOCATION)
@patch("epplib.models.common.DomainAuthInfo.namespace", NAMESPACE.NIC_DOMAIN)
class TestUpdateDomainDNSSECExtension(XMLTestCase):
    addKeyData = {
        "flags": 250,
        "protocol": 2,
        "alg": 0,
        "pubKey": "vPup3limpJ7VChFaNJky+A==",
    }
    addDsData = {
        "keyTag": 1234,
        "alg": 1,
        "digestType": 3,
        "digest": "ec0bdd990b39feead889f0ba613db4ad",
        "keyData": DNSSECKeyData(**addKeyData),
    }
    updateParams = {
        "maxSigLife": 1222,
        "remDsData": paramsWithMultiDsData["dsData"],
        "dsData": [DSData(**addDsData), paramsWithMultiDsData["dsData"][1]],
    }

    def setUp(self) -> None:
        """Setup params."""
        self.params = {
            "name": "mydoma.in",
            "auth_info": DomainAuthInfo(pw="2fooBAR123fooBaz"),
        }

    def test_data_with_dsData(self):
        extension = UpdateDomainDNSSECExtension(**self.updateParams)
        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )

        expected = EM.update(
            EM.rem(
                EM.dsData(
                    EM.keyTag(str(dsDataDict["keyTag"])),
                    EM.alg(str(dsDataDict["alg"])),
                    EM.digestType(str(dsDataDict["digestType"])),
                    EM.digest(dsDataDict["digest"]),
                    EM.keyData(
                        EM.flags(str(keyDataDict["flags"])),
                        EM.protocol(str(keyDataDict["protocol"])),
                        EM.alg(str(keyDataDict["alg"])),
                        EM.pubKey(str(keyDataDict["pubKey"])),
                    ),
                ),
                EM.dsData(
                    EM.keyTag(str(dsDataIncomplete["keyTag"])),
                    EM.alg(str(dsDataIncomplete["alg"])),
                    EM.digestType(str(dsDataIncomplete["digestType"])),
                    EM.digest(dsDataIncomplete["digest"]),
                ),
            ),
            EM.add(
                EM.dsData(
                    EM.keyTag(str(self.addDsData["keyTag"])),
                    EM.alg(str(self.addDsData["alg"])),
                    EM.digestType(str(self.addDsData["digestType"])),
                    EM.digest(self.addDsData["digest"]),
                    EM.keyData(
                        EM.flags(str(self.addKeyData["flags"])),
                        EM.protocol(str(self.addKeyData["protocol"])),
                        EM.alg(str(self.addKeyData["alg"])),
                        EM.pubKey(str(self.addKeyData["pubKey"])),
                    ),
                ),
                EM.dsData(
                    EM.keyTag(str(dsDataIncomplete["keyTag"])),
                    EM.alg(str(dsDataIncomplete["alg"])),
                    EM.digestType(str(dsDataIncomplete["digestType"])),
                    EM.digest(dsDataIncomplete["digest"]),
                ),
            ),
            EM.chg(EM.maxSigLife(str(self.updateParams["maxSigLife"]))),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_data_with_removeAll(self):
        extension = UpdateDomainDNSSECExtension(remAllDsKeyData=True)
        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )

        expected = EM.update(EM.rem(EM.all("true")))
        self.assertXMLEqual(extension.get_payload(), expected)

    def test_data_with_keydata(self):
        updateParamsKeyData = {
            "remKeyData": paramsWithKeyData["keyData"],
            "keyData": [DNSSECKeyData(**self.addKeyData)],
        }
        extension = UpdateDomainDNSSECExtension(**updateParamsKeyData)

        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )
        expected = EM.update(
            EM.rem(
                EM.keyData(
                    EM.flags(str(keyDataDict["flags"])),
                    EM.protocol(str(keyDataDict["protocol"])),
                    EM.alg(str(keyDataDict["alg"])),
                    EM.pubKey(str(keyDataDict["pubKey"])),
                )
            ),
            EM.add(
                EM.keyData(
                    EM.flags(str(self.addKeyData["flags"])),
                    EM.protocol(str(self.addKeyData["protocol"])),
                    EM.alg(str(self.addKeyData["alg"])),
                    EM.pubKey(str(self.addKeyData["pubKey"])),
                )
            ),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_data_with_mulit_keydata(self):
        updateParamsMultiKeyData = {
            "remKeyData": paramsWithKeyData["keyData"],
            "keyData": [DNSSECKeyData(**self.addKeyData)],
        }
        extension = UpdateDomainDNSSECExtension(
            remKeyData=[DNSSECKeyData(**keyDataDict)],
            keyData=[DNSSECKeyData(**self.addKeyData), DNSSECKeyData(**keyDataDict2)],
        )

        EM = ElementMaker(
            namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS}
        )
        expected = EM.update(
            EM.rem(
                EM.keyData(
                    EM.flags(str(keyDataDict["flags"])),
                    EM.protocol(str(keyDataDict["protocol"])),
                    EM.alg(str(keyDataDict["alg"])),
                    EM.pubKey(str(keyDataDict["pubKey"])),
                )
            ),
            EM.add(
                EM.keyData(
                    EM.flags(str(self.addKeyData["flags"])),
                    EM.protocol(str(self.addKeyData["protocol"])),
                    EM.alg(str(self.addKeyData["alg"])),
                    EM.pubKey(str(self.addKeyData["pubKey"])),
                ),
                EM.keyData(
                    EM.flags(str(keyDataDict2["flags"])),
                    EM.protocol(str(keyDataDict2["protocol"])),
                    EM.alg(str(keyDataDict2["alg"])),
                    EM.pubKey(str(keyDataDict2["pubKey"])),
                ),
            ),
        )

        self.assertXMLEqual(extension.get_payload(), expected)

    def test_valid_no_extension(self):
        self.assertRequestValid(UpdateDomain, self.params, schema=SCHEMA)

    def test_valid(self):
        extension = UpdateDomainDNSSECExtension(**self.updateParams)
        self.assertRequestValid(
            UpdateDomain, self.params, extension=extension, schema=SCHEMA
        )


class TestDNSSECExtension(TestCase):
    EM = ElementMaker(namespace=NAMESPACE.SEC_DNS, nsmap={"secDNS": NAMESPACE.SEC_DNS})

    def test_extract_with_DsData(self):
        element = self.EM.infData(
            self.EM.maxSigLife(str(paramsWithMultiDsData["maxSigLife"])),
            self.EM.dsData(
                self.EM.keyTag(str(dsDataDict["keyTag"])),
                self.EM.alg(str(dsDataDict["alg"])),
                self.EM.digestType(str(dsDataDict["digestType"])),
                self.EM.digest(dsDataDict["digest"]),
                self.EM.keyData(
                    self.EM.flags(str(keyDataDict["flags"])),
                    self.EM.protocol(str(keyDataDict["protocol"])),
                    self.EM.alg(str(keyDataDict["alg"])),
                    self.EM.pubKey(str(keyDataDict["pubKey"])),
                ),
            ),
            self.EM.dsData(
                self.EM.keyTag(str(dsDataIncomplete["keyTag"])),
                self.EM.alg(str(dsDataIncomplete["alg"])),
                self.EM.digestType(str(dsDataIncomplete["digestType"])),
                self.EM.digest(dsDataIncomplete["digest"]),
            ),
        )

        result = DNSSECExtension.extract(element)
        expected = DNSSECExtension(**paramsWithMultiDsData)

        self.assertEqual(result, expected)

    def test_extract_with_maxSig(self):
        element = self.EM.infData(
            self.EM.maxSigLife(str(paramsWithMultiDsData["maxSigLife"]))
        )

        result = DNSSECExtension.extract(element)
        expected = DNSSECExtension(maxSigLife=paramsWithMultiDsData["maxSigLife"])
        self.assertEqual(result, expected)

    def test_extract_with_keyData(self):
        element = self.EM.infData(
            self.EM.keyData(
                self.EM.flags(str(keyDataDict["flags"])),
                self.EM.protocol(str(keyDataDict["protocol"])),
                self.EM.alg(str(keyDataDict["alg"])),
                self.EM.pubKey(str(keyDataDict["pubKey"])),
            )
        )
        result = DNSSECExtension.extract(element)
        expected = DNSSECExtension(keyData=[DNSSECKeyData(**keyDataDict)])
        self.assertEqual(result, expected)

    def test_extract_with_multi_keyData(self):
        element = self.EM.infData(
            self.EM.keyData(
                self.EM.flags(str(keyDataDict["flags"])),
                self.EM.protocol(str(keyDataDict["protocol"])),
                self.EM.alg(str(keyDataDict["alg"])),
                self.EM.pubKey(str(keyDataDict["pubKey"])),
            ),
            self.EM.keyData(
                self.EM.flags(str(keyDataDict2["flags"])),
                self.EM.protocol(str(keyDataDict2["protocol"])),
                self.EM.alg(str(keyDataDict2["alg"])),
                self.EM.pubKey(str(keyDataDict2["pubKey"])),
            ),
        )
        result = DNSSECExtension.extract(element)
        expected = DNSSECExtension(
            keyData=[DNSSECKeyData(**keyDataDict), DNSSECKeyData(**keyDataDict2)]
        )
        self.assertEqual(result, expected)
