# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import filecmp
import mock

from mock import Mock, MagicMock
from balancer.drivers.haproxy.HaproxyDriver import HaproxyConfigFile
from balancer.drivers.haproxy.HaproxyDriver import HaproxyFronted
from balancer.drivers.haproxy.HaproxyDriver import HaproxyBackend
from balancer.drivers.haproxy.HaproxyDriver import HaproxyRserver
from balancer.drivers.haproxy.HaproxyDriver import HaproxyListen
from balancer.drivers.haproxy.HaproxyDriver import HaproxyDriver
from balancer.drivers.haproxy.RemoteControl import RemoteConfig
from balancer.drivers.haproxy.RemoteControl import RemoteService
from balancer.drivers.haproxy.RemoteControl import RemoteInterface
from balancer.drivers.haproxy.RemoteControl import RemoteSocketOperation

device_fake = {'ip': '192.168.19.86',
    'port': '22',
    'user': 'user',
    'password': 'swordfish',
    'extra': {'interface': 'eth0',
    'socket': '/tmp/haproxy.sock',
    'remote_conf_dir': '/etc/haproxy',
    'remote_conf_file': 'haproxy.cfg'}}
#
rserver = {'id': 'test_real_server',
           'address': '123.123.123.123', 'port': '9090',
           'weight': '8',  'maxCon': '30000'}
#
server_farm = {'id': 'SFname',  'type': 'HashAddrPredictor'}
#
virtualserver = {'id': 'VirtualServer',
                 'address': '115.115.115.115',
                 'port': '8080'}
#
probe = {'type': 'http',  'requestMethodType': 'GET',
         'requestHTTPurl': '/index.html',
         'minExpectStatus': '200'}
#
frontend = HaproxyFronted()
frontend.bind_address = '1.1.1.1'
frontend.bind_port = '8080'
frontend.default_backend = 'server_farm'
frontend.name = 'test_frontend'
#
backend = HaproxyBackend()
backend.name = 'test_backend'
backend.balance = 'source'
#
haproxy_rserver = HaproxyRserver()
haproxy_rserver.name = "new_test_server"
haproxy_rserver.address = '15.15.15.15'
haproxy_rserver.port = '123'
haproxy_rserver.fall = '10'
haproxy_rserver1 = HaproxyRserver()
haproxy_rserver1.name = "new_test_server_2"
haproxy_rserver1.address = '25.25.25.25'
haproxy_rserver1.port = '12345'
haproxy_rserver1.fall = '11'


class TestHaproxyDriverRemoteConfig (unittest.TestCase):
    def setUp(self):
        self.remote_config = RemoteConfig(device_fake, '/tmp',
                        '/etc/haproxy', 'haproxy.conf')
        self.remote_config.ssh = Mock()

    def test_get_config(self):
        self.assertTrue(self.remote_config.get_config())

    def test_put_config(self):
        self.assertTrue(self.remote_config.put_config())

    def test_validate_config_bad(self):
        file_channel = MagicMock(spec=file)
        self.remote_config.ssh.exec_command.return_value = [file_channel,
                                              file_channel, file_channel]
        self.assertFalse(self.remote_config.validate_config())


class TestHaproxyDriverRemoteService (unittest.TestCase):
    def setUp(self):
        self.remote_service = RemoteService(device_fake)
        self.remote_service.ssh = Mock()

    def test_start_service(self):
        self.assertTrue(self.remote_service.start())

    def test_stop_service(self):
        self.assertTrue(self.remote_service.stop())

    def test_restart_service(self):
        self.assertTrue(self.remote_service.restart())


class TestHaproxyDriverRemoteInterface (unittest.TestCase):
    def setUp(self):
        self.remote_interface = RemoteInterface(device_fake, frontend)
        self.remote_interface.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_interface.ssh.exec_command.return_value = [file_channel,
                                                 file_channel, file_channel]

    def test_add_ip(self):
        self.assertTrue(self.remote_interface.add_ip())

    def test_del_ip(self):
        self.assertTrue(self.remote_interface.del_ip())


class TestHaproxyDriverRemoteSocketOperation (unittest.TestCase):
    def setUp(self):
        self.remote_socket = RemoteSocketOperation(device_fake,
                                                backend, rserver)
        self.remote_socket.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_socket.ssh.exec_command.return_value = [file_channel,
                                                file_channel, file_channel]

    def test_suspend_server(self):
        self.assertTrue(self.remote_socket.suspend_server())

    def test_activate_server(self):
        self.assertTrue(self.remote_socket.activate_server())

    def test_get_statistics(self):
        self.assertTrue(self.remote_socket.get_statistics())


if __name__ == "__main__":
    unittest.main()