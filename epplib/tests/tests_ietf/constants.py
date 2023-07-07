from lxml.etree import XMLSchema
from pathlib import Path
from types import SimpleNamespace

NAMESPACE = SimpleNamespace(
    EPP="urn:ietf:params:xml:ns:epp-1.0",
    XSI="http://www.w3.org/2001/XMLSchema-instance",
    FRED="noop",
    NIC_CONTACT="urn:ietf:params:xml:ns:contact-1.0",
    NIC_DOMAIN="urn:ietf:params:xml:ns:domain-1.0",
    NIC_ENUMVAL="noop",
    NIC_EXTRA_ADDR="noop",
    NIC_HOST="urn:ietf:params:xml:ns:host-1.0",
    NIC_KEYSET="noop",
    NIC_NSSET="noop",
)

SCHEMA_LOCATION = SimpleNamespace(
    XSI="urn:ietf:params:xml:ns:epp-1.0 epp-1.0.xsd",
    FRED="noop fred-1.5.0.xsd",
    NIC_CONTACT="urn:ietf:params:xml:ns:contact-1.0 contact-1.0.xsd",
    NIC_DOMAIN="urn:ietf:params:xml:ns:domain-1.0 domain-1.0.xsd",
    NIC_ENUMVAL="noop enumval-1.2.0.xsd",
    NIC_EXTRA_ADDR="noop extra-addr-1.0.0.xsd",
    NIC_HOST="urn:ietf:params:xml:ns:host-1.0 host-1.0.xsd",
    NIC_KEYSET="noop keyset-1.3.2.xsd",
    NIC_NSSET="noop nsset-1.2.2.xsd",
)

BASE_DATA_PATH = Path(__file__).parent / "data"
SCHEMA = XMLSchema(file=str(BASE_DATA_PATH / "schemas/all-1.0.xsd"))
