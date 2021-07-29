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

import sys
from multiprocessing import Event, Pipe, Process, synchronize
from multiprocessing.connection import Connection
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket
from typing import Optional
from unittest import TestCase
from unittest.mock import patch

from epplib.transport import SocketTransport, TransportError

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import TypedDict
else:  # pragma: no cover
    from typing_extensions import TypedDict

BASE_DATA_PATH = Path(__file__).parent / 'data'
Params = TypedDict('Params', {
    'hostname': str,
    'port': int,
    'cert_file': Optional[Path],
    'key_file': Optional[Path],
    'password': Optional[str],
})


def server(
    hostname: str, port: int, server_ready: synchronize.Event, pipe: Connection = None, message: bytes = None,
):  # pragma: no cover
    with socket(AF_INET, SOCK_STREAM) as listening:
        listening.bind((hostname, port))
        listening.listen()
        server_ready.set()
        connection, _ = listening.accept()

        with connection:
            if message:
                message_length = (len(message) + 4).to_bytes(4, 'big')
                connection.sendall(message_length + message)
            received = connection.recv(1024)
            if pipe is not None:
                pipe.send(received)


class TestSocketTransport(TestCase):

    params: Params = {
        'hostname': 'localhost',
        'port': 64000,
        'cert_file': BASE_DATA_PATH / 'test_cert.pem',
        'key_file': BASE_DATA_PATH / 'test_cert.pem',
        'password': 'letmein',
    }

    @patch('epplib.transport.ssl.create_default_context')
    @patch('epplib.transport.socket.create_connection')
    def test_connect_close(self, create_connection_mock, create_context_mock):
        transport = SocketTransport(**self.params)
        transport.connect()
        transport.close()

        context = create_context_mock.return_value

        context.load_cert_chain.assert_called_once_with(
            certfile=self.params['cert_file'],
            keyfile=self.params['key_file'],
            password=self.params['password'],
        )
        context.wrap_socket.assert_called_once_with(
            create_connection_mock.return_value,
            server_hostname=self.params['hostname']
        )
        create_connection_mock.assert_called_once_with((self.params['hostname'], self.params['port']))
        context.wrap_socket.return_value.close.assert_called_once_with()

    @patch('epplib.transport.ssl.create_default_context')
    @patch('epplib.transport.socket.create_connection')
    def test_connect_no_cert(self, create_connection_mock, create_context_mock):
        params: Params = {
            'hostname': 'localhost',
            'port': 64000,
            'cert_file': None,
            'key_file': None,
            'password': None,
        }
        transport = SocketTransport(**params)
        transport.connect()
        transport.close()

        context = create_context_mock.return_value

        context.load_cert_chain.assert_not_called()
        context.wrap_socket.assert_called_once_with(
            create_connection_mock.return_value,
            server_hostname=self.params['hostname']
        )
        create_connection_mock.assert_called_once_with((self.params['hostname'], self.params['port']))
        context.wrap_socket.return_value.close.assert_called_once_with()

    @patch('epplib.transport.ssl.create_default_context', autospec=True)
    def test_send(self, context_mock):
        context_mock.return_value.wrap_socket = lambda x, **kwargs: x
        server_ready = Event()
        pipe_client, pipe_server = Pipe()

        server_args = {
            'hostname': self.params['hostname'],
            'port': self.params['port'],
            'server_ready': server_ready,
            'pipe': pipe_server,
        }
        process = Process(target=server, kwargs=server_args)
        process.start()

        server_ready.wait()
        transport = SocketTransport(**self.params)
        transport.connect()
        message = b'Message!'
        transport.send(message)
        transport.close()

        process.join()
        message_length = (len(message) + 4).to_bytes(4, 'big')
        self.assertEqual(pipe_client.recv(), message_length + message)

    @patch('epplib.transport.ssl.create_default_context', autospec=True)
    def test_receive(self, context_mock):
        context_mock.return_value.wrap_socket = lambda x, **kwargs: x
        server_ready = Event()

        message = b'Message!'

        server_args = {
            'hostname': self.params['hostname'],
            'port': self.params['port'],
            'server_ready': server_ready,
            'message': message,
        }
        process = Process(target=server, kwargs=server_args)
        process.start()

        server_ready.wait()
        transport = SocketTransport(**self.params)
        transport.connect()
        received = transport.receive()
        transport.close()

        process.join()
        self.assertEqual(received, message)

    def test_not_connected(self):
        transport = SocketTransport(**self.params)

        with self.assertRaisesRegex(TransportError, 'Not connected to the server\\.'):
            transport.receive()
        with self.assertRaisesRegex(TransportError, 'Not connected to the server\\.'):
            transport.send(b'Message!')

    @patch('epplib.transport.ssl.create_default_context', autospec=True)
    def test_socket_closed(self, context_mock):
        context_mock.return_value.wrap_socket = lambda x, **kwargs: x
        server_ready = Event()

        server_args = {
            'hostname': self.params['hostname'],
            'port': self.params['port'],
            'server_ready': server_ready,
        }
        process = Process(target=server, kwargs=server_args)
        process.start()

        server_ready.wait()

        transport = SocketTransport(**self.params)
        transport.connect()
        transport.close()

        with self.assertRaisesRegex(TransportError, 'Socket closed\\.'):
            transport.receive()
        with self.assertRaisesRegex(TransportError, 'Socket closed\\.'):
            transport.send(b'Message!')

    def test_close_before_connecting(self):
        transport = SocketTransport(**self.params)
        transport.close()
