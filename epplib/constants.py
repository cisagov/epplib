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

"""Constants shared accross epplib."""

from types import SimpleNamespace

NAMESPACE = SimpleNamespace(
    EPP="urn:ietf:params:xml:ns:epp-1.0",
    XSI="http://www.w3.org/2001/XMLSchema-instance",
    FRED="http://www.nic.cz/xml/epp/fred-1.5",
    NIC_CONTACT="http://www.nic.cz/xml/epp/contact-1.6",
    NIC_DOMAIN="http://www.nic.cz/xml/epp/domain-1.4",
    NIC_ENUMVAL="http://www.nic.cz/xml/epp/enumval-1.2",
    NIC_EXTRA_ADDR="http://www.nic.cz/xml/epp/extra-addr-1.0",
    NIC_HOST="urn:ietf:params:xml:ns:host-1.0",
    NIC_KEYSET="http://www.nic.cz/xml/epp/keyset-1.3",
    NIC_NSSET="http://www.nic.cz/xml/epp/nsset-1.2",
)
SCHEMA_LOCATION = SimpleNamespace(
    XSI="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd",
    FRED="http://www.nic.cz/xml/epp/fred-1.5 fred-1.5.0.xsd",
    NIC_CONTACT="http://www.nic.cz/xml/epp/contact-1.6 contact-1.6.2.xsd",
    NIC_DOMAIN="http://www.nic.cz/xml/epp/domain-1.4 domain-1.4.2.xsd",
    NIC_ENUMVAL="http://www.nic.cz/xml/epp/enumval-1.2 enumval-1.2.0.xsd",
    NIC_EXTRA_ADDR="http://www.nic.cz/xml/epp/extra-addr-1.0 extra-addr-1.0.0.xsd",
    NIC_HOST="urn:ietf:params:xml:ns:host-1.0 host-1.0.xsd",
    NIC_KEYSET="http://www.nic.cz/xml/epp/keyset-1.3 keyset-1.3.2.xsd",
    NIC_NSSET="http://www.nic.cz/xml/epp/nsset-1.2 nsset-1.2.2.xsd",
)
