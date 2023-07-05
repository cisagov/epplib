from datetime import date
from unittest import TestCase

from lxml.builder import ElementMaker
from typing import Any,Mapping
from epplib.constants import NAMESPACE

from epplib.models.common import DSData, SecDNSKeyData
from epplib.responses.extensions import SecDNSExtension


class TestSecDnsExtension(TestCase):
    keyDataDict={'flags':257,
                    'protocol':3,
                    'alg':1,
                    'pubKey':'AQPJ////4Q=='}
    dsDataDict={
            'keyTag':12345,
            'alg':3,
            'digestType':1,
            'digest':'49FD46E6C4B45C55D4AC',
            'keyData':SecDNSKeyData(**keyDataDict)
            }
    paramsWithDsData:Mapping[str, Any] = {
        'maxSigLife': 3215,
        'dsData':DSData(**dsDataDict)
    }
    EM = ElementMaker(namespace=NAMESPACE.SEC_DNS,nsmap={"secDNS":NAMESPACE.SEC_DNS})

    def test_extract_with_DsData(self):
        element = self.EM.infData(self.EM.maxSigLife(str(self.paramsWithDsData['maxSigLife'])),
            self.EM.dsData(
                self.EM.keyTag(str(self.dsDataDict['keyTag'])),
                self.EM.alg(str(self.dsDataDict['alg'])),
                self.EM.digestType(str(self.dsDataDict['digestType'])),
                self.EM.digest(self.dsDataDict['digest']),
                self.EM.keyData(
                            self.EM.flags(str(self.keyDataDict['flags'])),
                            self.EM.protocol(str(self.keyDataDict['protocol'])),
                            self.EM.alg(str(self.keyDataDict['alg'])),
                            self.EM.pubKey(str(self.keyDataDict['pubKey']))
                           )
            ))

        result = SecDNSExtension.extract(element)

        expected = SecDNSExtension(**self.paramsWithDsData)
        self.assertEqual(result, expected)
        
    def test_extract_with_maxSig(self):

        element = self.EM.infData(self.EM.maxSigLife(str(self.paramsWithDsData['maxSigLife'])))


        result = SecDNSExtension.extract(element)
        expected = SecDNSExtension(maxSigLife=self.paramsWithDsData['maxSigLife'])
        self.assertEqual(result, expected)


    def test_extract_with_keyData(self):
        element = self.EM.infData(
                self.EM.keyData(
                    self.EM.flags(str(self.keyDataDict['flags'])),
                    self.EM.protocol(str(self.keyDataDict['protocol'])),
                    self.EM.alg(str(self.keyDataDict['alg'])),
                    self.EM.pubKey(str(self.keyDataDict['pubKey']))
                    )
            )
        result = SecDNSExtension.extract(element)
        expected = SecDNSExtension(keyData=SecDNSKeyData(** self.keyDataDict))
        self.assertEqual(result, expected)