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

"""Module providing EPP command extensions."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar,Optional, Sequence
from datetime import date

from lxml.etree import Element, QName, SubElement
from lxml import etree
from epplib.constants import NAMESPACE, SCHEMA_LOCATION
from epplib.models import ExtraAddr, DSData, SecDNSKeyData


class CommandExtension(ABC):
    """Base class for Command extensions."""

    @abstractmethod
    def get_payload(self) -> Element:
        """Create EPP Elements specific to the given Extension."""


@dataclass
class CreateContactMailingAddressExtension(CommandExtension):
    """Mailing address extension for Create contact command.

    Attributes:
        addr: Content of extension/create/mailing/addr element.
    """

    addr: ExtraAddr

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateContactMailingAddressExtension."""
        create = Element(QName(NAMESPACE.NIC_EXTRA_ADDR, 'create'))
        create.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_EXTRA_ADDR)
        mailing = SubElement(create, QName(NAMESPACE.NIC_EXTRA_ADDR, 'mailing'))
        mailing.append(self.addr.get_payload())
        return create

@dataclass
class CreateDomainSecDNSExtension(CommandExtension):
    """Sec DNS Extension for Create Domain command.

    Attributes:
        maxSigLife: Content of extension/create/secDNS/maxSigLife.
        dsData:  Content of extension/create/secDNS/dsData.
        keyData:  Content of extension/create/secDNS/keyData.
    """

    maxSigLife: Optional[int] =None
    dsData: Optional[Sequence[DSData]] = None 
    keyData: Optional[Sequence[SecDNSKeyData]] = None
    
    def get_payload(self) -> Element:
 
        create =Element(QName(NAMESPACE.SEC_DNS, "create"), nsmap={"secDNS":NAMESPACE.SEC_DNS})
    
        if not self.maxSigLife is None:
            SubElement(create,QName(NAMESPACE.SEC_DNS, "maxSigLife")).text = str(self.maxSigLife)

        #can't have both dsdata and keydata, one or the the other or none
        if  not self.dsData is None:
            for dsDataObj in self.dsData:
                create.append(dsDataObj.get_payload())
        elif not self.keyData is None:
            for keyDataObj in self.keyData:
                create.append(keyDataObj.get_payload())

        return create
@dataclass
class UpdateDomainSecDNSExtension(CommandExtension):
    maxSigLife: Optional[int] =None
    dsData: Optional[DSData] = None
    keyData: Optional[SecDNSKeyData] =None
    remDsData:Optional[DSData] = None #should be a list to add
    remKeyData:Optional[SecDNSKeyData] =None #should be a list to remove
    remAllDsKeyData: Optional[bool]=False

    def _make_remove_element(self, element: Element)->Element:
        return SubElement(element,QName(NAMESPACE.SEC_DNS, "rem"))
    def get_payload(self) -> Element:
 
        update =Element(QName(NAMESPACE.SEC_DNS, "update"), nsmap={"secDNS":NAMESPACE.SEC_DNS})
    
       
        #remove elmements need to preceed the add elements, don't move this order
        if self.remAllDsKeyData:
            remAll=self._make_remove_element(update)
            SubElement(remAll,QName(NAMESPACE.SEC_DNS, "all")).text = "true"

        elif not self.remDsData is None: #change when made a list?
            remDsElement=self._make_remove_element(update)
            
            for remDsDataObj in self.remDsData:  
                remDsElement.append(remDsDataObj.get_payload())
        
        elif  not self.remKeyData is None: #change when made a list?
            remKeyElement=self._make_remove_element(update)
            for remKeyDataObj in self.remKeyData:
                remKeyElement.append(remKeyDataObj.get_payload())
        
        if  not self.dsData is None: 
            addElement=SubElement(update,QName(NAMESPACE.SEC_DNS, "add"))

            for dsDataObj in self.dsData:
                addElement.append(dsDataObj.get_payload())
        elif  not self.keyData is None: 
            addElement=SubElement(update,QName(NAMESPACE.SEC_DNS, "add"))

            for keyDataObj in self.keyData:
                addElement.append(keyDataObj.get_payload())  
       
        if not self.maxSigLife is None: 
            
            changeElement=SubElement(update,QName(NAMESPACE.SEC_DNS, "chg"))
            SubElement(changeElement,QName(NAMESPACE.SEC_DNS, "maxSigLife")).text = str(self.maxSigLife)

        return update
    
@dataclass
class UpdateContactMailingAddressExtension(CommandExtension):
    """Mailing address extension for Update contact command.

    Attributes:
        addr: If set it makes the content of extension/update/set/mailing/addr element
              if None it causes extension/update/rem/mailing element to appear
    """

    addr: Optional[ExtraAddr]

    def get_payload(self) -> Element:
        """Create EPP Elements specific to CreateContactMailingAddressExtension."""
        update = Element(QName(NAMESPACE.NIC_EXTRA_ADDR, 'update'))
        update.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_EXTRA_ADDR)

        if self.addr is None:
            action = SubElement(update, QName(NAMESPACE.NIC_EXTRA_ADDR, 'rem'))
            SubElement(action, QName(NAMESPACE.NIC_EXTRA_ADDR, 'mailing'))
        else:
            action = SubElement(update, QName(NAMESPACE.NIC_EXTRA_ADDR, 'set'))
            mailing = SubElement(action, QName(NAMESPACE.NIC_EXTRA_ADDR, 'mailing'))
            mailing.append(self.addr.get_payload())
        return update


@dataclass
class EnumExtension(CommandExtension):
    """ENUM extension for Create Domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag: ClassVar[str]

    val_ex_date: Optional[date] = None
    publish: Optional[bool] = None

    def get_payload(self) -> Element:
        """Create EPP Elements specific to DomainEnumExtension."""
        root = Element(QName(NAMESPACE.NIC_ENUMVAL, self.tag))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_ENUMVAL)
        if self.val_ex_date is not None:
            expiration_date = SubElement(root, QName(NAMESPACE.NIC_ENUMVAL, 'valExDate'))
            expiration_date.text = str(self.val_ex_date)
        if self.publish is not None:
            SubElement(root, QName(NAMESPACE.NIC_ENUMVAL, 'publish')).text = str(self.publish).lower()
        return root


@dataclass
class CreateDomainEnumExtension(EnumExtension):
    """ENUM extension for Create domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag = 'create'


@dataclass
class RenewDomainEnumExtension(EnumExtension):
    """ENUM extension for Renew domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element.
        publish: Content of extension/create/publish element.
    """

    tag = 'renew'


@dataclass
class UpdateDomainEnumExtension(EnumExtension):
    """ENUM extension for Update Domain command.

    Attributes:
        val_ex_date: Content of extension/create/valExDate element
        publish: Content of extension/create/publish element
    """

    tag = 'update'

    def get_payload(self) -> Element:
        """Create EPP Elements specific to UpdateDomainEnumExtension."""
        root = Element(QName(NAMESPACE.NIC_ENUMVAL, self.tag))
        root.set(QName(NAMESPACE.XSI, 'schemaLocation'), SCHEMA_LOCATION.NIC_ENUMVAL)
        change = SubElement(root, QName(NAMESPACE.NIC_ENUMVAL, 'chg'))
        if self.val_ex_date is not None:
            expiration_date = SubElement(change, QName(NAMESPACE.NIC_ENUMVAL, 'valExDate'))
            expiration_date.text = str(self.val_ex_date)
        if self.publish is not None:
            SubElement(change, QName(NAMESPACE.NIC_ENUMVAL, 'publish')).text = str(self.publish).lower()
        return root
