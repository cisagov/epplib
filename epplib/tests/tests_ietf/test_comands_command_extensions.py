from typing import Any, Dict, Mapping, cast
from unittest.mock import patch
from lxml.builder import ElementMaker
from lxml import etree
from epplib import commands
from epplib.commands import CreateDomain
from epplib.commands.command_extensions import CreateDomainSecDNSExtension
from epplib.tests.tests_ietf.constants import NAMESPACE, SCHEMA_LOCATION, SCHEMA
from epplib.tests.utils import XMLTestCase
from epplib.models.common import DSData, DomainAuthInfo, SecDNSKeyData
print("top")
@patch('epplib.commands.create.NAMESPACE', NAMESPACE)
@patch('epplib.commands.create.SCHEMA_LOCATION', SCHEMA_LOCATION)
@patch('epplib.models.common.DomainAuthInfo.namespace', NAMESPACE.NIC_DOMAIN)
@patch('epplib.constants', NAMESPACE)
@patch('epplib.constants.SCHEMA_LOCATION', SCHEMA_LOCATION)
class TestCreateDomainSecDNS(XMLTestCase):
    command_params: Dict[str, Any] = {
        'name': 'thisdomain.cz',
        'registrant': 'CID-MYOWN',
        'auth_info': DomainAuthInfo(pw='2fooBAR123fooBaz'),
    }
    sig_params: Mapping[str, Any] = {
        'maxSigLife': 3215
    }
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
    params:Mapping[str, Any] = {
        'maxSigLife': 3215,
        'dsData':DSData(**dsDataDict)
    }

    def test_data(self):
        extension = CreateDomainSecDNSExtension(**self.params)
        print("********EXTENSIONT IS ******")
        print(etree.tostring(extension.get_payload(), pretty_print=False))
        EM = ElementMaker(namespace=NAMESPACE.SEC_DNS,nsmap={"secDNS":NAMESPACE.SEC_DNS})
        expected = EM.create(
            EM.maxSigLife(str(self.params['maxSigLife'])),
            EM.dsData(
                EM.keyTag(str(self.dsDataDict['keyTag'])),
                EM.alg(str(self.dsDataDict['alg'])),
                EM.digestType(str(self.dsDataDict['digestType'])),
                EM.digest(self.dsDataDict['digest']),
                EM.keyData(
                            EM.flags(str(self.keyDataDict['flags'])),
                            EM.protocol(str(self.keyDataDict['protocol'])),
                            EM.alg(str(self.keyDataDict['alg'])),
                            EM.pubKey(str(self.keyDataDict['pubKey']))
                           )
            )
        )
        print("********")
        print(etree.tostring(expected, pretty_print=False))
        print("********")

        self.assertXMLEqual(extension.get_payload(), expected)
    def test_valid(self):
        extension = CreateDomainSecDNSExtension(**self.params)
        request = CreateDomain(**self.command_params)
        cast(commands, request).add_extension(extension)
        xml = request.xml(tr_id='tr_id_123')
        print("~~~~~~~~~~~~~~")
        print(xml)
        parser = etree.XMLParser(no_network=True, resolve_entities=False)
        parsed = etree.fromstring(xml, parser=parser)  # nosec - It should be safe with resolve_entities=False.
        print("~~~~~*******")
        print("parsed class")

        # print(parsed.__class__)
        if parsed.getroottree().docinfo.doctype:
            print("error")
        print("~~~~~*******")
        print()
        r=CreateDomain(**self.command_params)
        cast(CreateDomain,request).add_extension(extension)
        xml=request.xml(tr_id="123")
        print(xml)
        self.assertRequestValid(CreateDomain, self.command_params, extension=extension,schema=SCHEMA)# extension=extension

