# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import filecmp
import mock

import balancer.drivers.haproxy.HaproxyDriver as Driver


device_fake1 = {'id': 'fake1',
                'type': 'FAKE',
                'version': '1',
                'ip': '10.0.0.10',
                'port': 1010,
                'user': 'user1',
                'password': 'secrete1',
                'extra': {'interface': 'eth0',
                'socket': '/tmp/haproxy.sock',
                'remote_conf_dir': '/etc/haproxy',
                'remote_conf_file': 'haproxy.cfg'}}

device_fake2 = {'id': 'fake2',
                'type': 'FAKE',
                'version': '2',
                'ip': '10.0.0.20',
                'port': 2020,
                'user': 'user2',
                'password': 'secrete2',
                'extra': {'interface': 'wlan10'}}

conf = []

def merge_dicts(dict1, dict2):
    result = dict1
    for i in dict2:
        result[i] = dict2[i]
    return result

def get_fake_rserver(id_, parameters):
    rserver = {'id': id_, 'weight': '8', 'address': '10.2.1.2', \
               'port': '4055', 'minCon': '100', 'maxCon': '2000'}
    return merge_dicts(rserver, parameters)

def get_fake_server_farm(id_, parameters):
    server_farm = {'id': id_, 'type': 'Host'}
    return merge_dicts(server_farm, parameters)

def get_fake_virtual_ip(id_, parameters):
    vip = {'id': id_, 'address': '100.1.1.1', 'port': '8801'}
    return merge_dicts(vip, parameters)

def get_fake_probe(id_, parameters):
    probe = {'id': id_, 'type': 'HTTP', 'requestMethodType': 'GET', \
             'requestHTTPUrl': '/index.html', 'minExpectStatus': '300'}
    return merge_dicts(probe, parameters)

def get_fake_predictor(id_, parameters):
    predictor = {'id': id_, 'type': 'roundrobin', 'extra': {}}
    return merge_dicts(predictor, parameters)

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


class TestHaproxyDriverRemoteConfig(unittest.TestCase):
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


class TestHaproxyDriverRemoteService(unittest.TestCase):
    def setUp(self):
        self.remote_service = RemoteService(device_fake)
        self.remote_service.ssh = Mock()
        a = Mock()
        a.file_channel = MagicMock(spec=file)
        self.remote_service.ssh.exec_command.return_value = [a, a, a]

    def test_start_service(self):
        self.remote_service.start()

    def test_stop_service(self):
        self.remote_service.stop()

    def test_restart_service(self):
        self.remote_service.restart()


class TestHaproxyDriverRemoteInterface(unittest.TestCase):
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


class TestHaproxyDriverRemoteSocketOperation(unittest.TestCase):
    def setUp(self):
        self.remote_socket = RemoteSocketOperation(device_fake,
                                                backend, rserver)
        self.remote_socket.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_socket.ssh.exec_command.return_value = [file_channel,
                                                file_channel, file_channel]

    def test_get_statistics(self):
        self.assertTrue(self.remote_socket.get_statistics())


class TestHaproxyDriverAllFunctions(unittest.TestCase):
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
