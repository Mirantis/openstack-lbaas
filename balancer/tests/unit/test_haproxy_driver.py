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
conf = []
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
probe_https = {'type': 'https',  'requestMethodType': 'GET',
         'requestHTTPurl': '/index.html',
         'minExpectStatus': '200'}

#
probe_tcp = {'type': 'tcp',  'requestMethodType': 'GET',
         'requestHTTPurl': '/index.html',
         'minExpectStatus': '200'}

#
a = {'type': 'roudrobin'}
a['extra'] = {}
predictor = [a, ]

#
a = {'type': 'leastconnections'}
a['extra'] = {}
predictor_connections = [a, ]

#
a = {'type': 'hashurl'}
a['extra'] = {}
predictor_hashurl = [a, ]

#
a = {'type': 'hashaddr'}
a['extra'] = {}
predictor_hashaddr = [a, ]

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
        file_channel = MagicMock(spec=file)
        self.remote_interface.ssh.exec_command.return_value = [file_channel,
                                                 file_channel, file_channel]

    def test_start_service(self):
        self.remote_service.start()

    def test_stop_service(self):
        self.remote_service.stop()

    def test_restart_service(self):
        self.remote_service.restart()


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

    def test_get_statistics(self):
        self.assertTrue(self.remote_socket.get_statistics())


class TestHaproxyDeriverAllFunctions (unittest.TestCase):
    def setUp(self):
        self.remote_socket = RemoteSocketOperation(device_fake,
                                                backend, rserver)
        self.remote_socket.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_socket.ssh.exec_command.return_value = [file_channel,
                                                file_channel, file_channel]
        self.driver = HaproxyDriver(conf, device_fake)

    def test_create_real_server(self):
        self.driver.create_real_server(haproxy_rserver)

    def test_delete_real_server(self):
        self.driver.delete_real_server(haproxy_rserver)

    def test_suspend_real_server(self):
        self.driver.suspend_real_server(server_farm, rserver)

    def test_activate_real_server(self):
        self.driver.activate_real_server(server_farm, rserver)

    def test_create_probe(self):
        self.driver.create_probe(probe)

    def test_create_probe_tcp(self):
        self.driver.create_probe(probe_tcp)

    def test_create_probe_https(self):
        self.driver.create_probe(probe_https)

    def test_delete_probe(self):
        self.driver.delete_probe(probe_tcp)

    def test_create_server_farm_with_round_robin(self):
        self.driver.create_server_farm(server_farm, predictor)

    def test_create_server_farm_with_leastconnections(self):
        self.driver.create_server_farm(server_farm, predictor_connections)

    def test_create_server_farm_with_hashaddr(self):
        self.driver.create_server_farm(server_farm, predictor_hashaddr)

    def test_create_server_farm_with_hashurl(self):
        self.driver.create_server_farm(server_farm, predictor_hashurl)

    def test_delete_server_farm(self):
        self.driver.delete_server_farm(server_farm)

    def test_add_real_server_to_server_farm(self):
        self.driver.add_real_server_to_server_farm(\
                        server_farm, rserver)

    def test_delete_real_server_from_server_farm(self):
        self.driver.delete_real_server_from_server_farm(server_farm, \
                                                        rserver)

    def test_create_virtual_ip(self):
        self.driver.create_virtual_ip(virtualserver, server_farm)

    def test_delete_virtual_ip(self):
        self.driver.delete_virtual_ip(virtualserver)

if __name__ == "__main__":
    unittest.main()
