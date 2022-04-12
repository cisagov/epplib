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

    hostname = 'localhost'
    port = 12345
    cert_file = 'path/to/cert.pem'
    key_file = 'path/to/key.pem'

    transport = SocketTransport(hostname, port, cert_file=cert_file, key_file=key_file)

    with Client(transport) as client:
        login = Login(cl_id='my_id', password='passwd', obj_uris=['http://www.nic.cz/xml/epp/contact-1.6'])
        response_login = client.send(login)
        print(response_login.code)

        info = InfoDomain(name='mydomain.cz')
        response_info = client.send(info)
        print(response_info.res_data.ex_date)

        client.send(Logout())
