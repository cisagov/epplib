===========
Fred-epplib
===========

Fred EPP library provides the means to communicate with an EPP server. It consists from four main modules: `client`,
`commands`, `responses`, and `models`.

The `Client` class in the `client` module is used to exchange the messages with the server. Module `commands` contains
the dataclasses representing the commands which may be sent to the server. `responses` module contains the dataclasses
representing the responses received from the server. `models` module contains dataclasses which are used to compose both
requests and responses.

For more details plese refer to the source code documentation. We suggest starting with the `Client` class in
the `client` module.

Usage
=====

In order to exchange messages with the server a `Transport` instance has to be created and passed to the init of
the `Client`. Then the `Client` is connected to the server using context manager or manually by calling the `connect`
method. The commands are created as the instances of the `Request` base class and send via the `send` method of
the `Client` instance. The response from the server is returned by `send` as an instance of the `Response` class. After
response is received its data may be examined.

See the example below

.. code-block:: python

    from epplib.client import Client
    from epplib.commands import InfoDomain, Login, Logout
    from epplib.transport import SocketTransport

    hostname = 'localhost'
    cert_file = 'path/to/cert.pem'
    key_file = 'path/to/key.pem'

    transport = SocketTransport(hostname, cert_file=cert_file, key_file=key_file)

    with Client(transport) as client:
        login = Login(cl_id='my_id', password='passwd', obj_uris=['http://www.nic.cz/xml/epp/contact-1.6'])
        response_login = client.send(login)
        print(response_login.code)

        info = InfoDomain(name='mydomain.cz')
        response_info = client.send(info)
        print(response_info.res_data[0].ex_date)

        client.send(Logout())

When using this library with a registry other than Fred, the XML schema must be changed before importing.
Fred EPP library is tested with Fred and isn't guaranteed to work with anything else.

.. code-block:: python

    # __init__.py

    NAMESPACE = SimpleNamespace(
        ...
        NIC_DOMAIN="urn:ietf:params:xml:ns:domain-1.0",
        ...
    )

    SCHEMA_LOCATION = SimpleNamespace(
        ...
        NIC_DOMAIN="urn:ietf:params:xml:ns:domain-1.0 domain-1.0.xsd",
        ...
    )

    from epplib import constants

    constants.NAMESPACE = NAMESPACE
    constants.SCHEMA_LOCATION = SCHEMA_LOCATION


Testing Code Locally
====================
gather dependencies
1. install python 3.10 or newer
2. optional setup up virtual envirornment
    -make virtual envirornment in the the terminal with:
     `python -m venv env`
    - activate the virtual envirornment in the terminal with:
     `source env/bin/activate``
3. install python dependencies
    `python -m pip install -r requirements.txt``


To run all the unittests in the library, open terminal and navigate to the outerdirectory where this readme is located. Then run
`python -m unittest`

To run unittests on a single file modify the above command by adding the name of the file to test such as:
`python3 -m unittest ./epplib/tests/tests_ietf/test_extensions.py`


Optional Code formatter
====================
Simply use the built in `black` code formatter that which will catch common linting issues
Run it using "black ."