# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import filecmp

import time

from mock import Mock, MagicMock

import balancer.drivers.haproxy.HaproxyDriver as Driver
import balancer.drivers.haproxy.RemoteControl as RemoteControl


device_fake = {'id': 'fake1',
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


def get_fake_HaproxyFrontend(id_):
    frontend = Driver.HaproxyFronted()
    frontend.bind_address = '1.1.1.1'
    frontend.bind_port = '8080'
    frontend.default_backend = 'server_farm'
    frontend.name = id_
    return frontend


def get_fake_HaproxyBackend(id_):
    backend = Driver.HaproxyBackend()
    backend.name = id_
    backend.balance = 'source'
    return backend


def get_fake_Haproxy_rserver(id_):
    haproxy_rserver = Driver.HaproxyRserver()
    haproxy_rserver.name = id_
    haproxy_rserver.address = '150.153.152.151'
    haproxy_rserver.port = '12663'
    haproxy_rserver.fall = '10'
    return haproxy_rserver


class TestHaproxyDriverRemoteConfig(unittest.TestCase):
    def setUp(self):
        self.remote_config = RemoteControl.RemoteConfig(device_fake, '/tmp',
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
        self.remote_service = RemoteControl.RemoteService(device_fake)
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
        self.frontend = get_fake_HaproxyFrontend('test')
        self.remote_interface = RemoteControl.RemoteInterface(device_fake)
        self.remote_interface.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_interface.ssh.exec_command.return_value = [file_channel,
                                                 file_channel, file_channel]

    def test_add_ip(self):
        self.assertTrue(self.remote_interface.add_ip(self.frontend))

    def test_del_ip(self):
        self.assertTrue(self.remote_interface.del_ip(self.frontend))


class TestHaproxyDriverRemoteSocketOperation(unittest.TestCase):
    def setUp(self):
        self.remote_socket = RemoteControl.RemoteSocketOperation(device_fake)
        self.remote_socket.ssh = Mock()
        file_channel = MagicMock(spec=file)
        self.remote_socket.ssh.exec_command.return_value = [file_channel,
                                                file_channel, file_channel]

    def test_get_statistics(self):
        self.assertTrue(self.remote_socket.get_statistics())


class TestHaproxyDriverAllFunctions(unittest.TestCase):
    def setUp(self):
        self.driver = Driver.HaproxyDriver(conf, device_fake)
        self.driver.config_file = Mock()
        self.driver.remote_config = Mock()

        self.driver.remote_socket = \
                    RemoteControl.RemoteSocketOperation(device_fake)
        a = Mock()
        a.file_channel = MagicMock(spec=file)
        self.driver.remote_socket.ssh = Mock()
        self.driver.remote_socket.ssh.exec_command.return_value = [a, a, a]

        self.driver.remote_interface = RemoteInterface(self.device_ref)
        self.driver.remote_interface.ssh = Mock()

    def test_create_real_server(self):
        ha_rserver = get_fake_Haproxy_rserver('Test_Rserver')
        self.driver.create_real_server(ha_rserver)

    def test_delete_real_server(self):
        ha_rserver = get_fake_Haproxy_rserver('test01')
        self.driver.delete_real_server(ha_rserver)

    def test_suspend_real_server(self):
        server_farm = get_fake_server_farm('sf-01', {})
        rserver = get_fake_server_farm('real_server1', {'port': 950})
        self.driver.suspend_real_server(server_farm, rserver)

    def test_activate_real_server(self):
        server_farm = get_fake_server_farm('sf-02', {})
        rserver = get_fake_server_farm('real_server2', {'maxCon': 40000})
        self.driver.activate_real_server(server_farm, rserver)

    def test_create_probe(self):
        probe = get_fake_probe('test-0002', {})
        self.driver.create_probe(probe)

    def test_create_probe_tcp(self):
        probe_tcp = get_fake_probe('test-0002', {})
        self.driver.create_probe(probe_tcp)

    def test_create_probe_https(self):
        probe_https = get_fake_probe('test-0002', {})
        self.driver.create_probe(probe_https)

    def test_delete_probe(self):
        probe_tcp = get_fake_probe('test-0002', {})
        self.driver.delete_probe(probe_tcp)

    def test_create_server_farm_with_round_robin(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor = get_fake_predictor('testPredictor01',
                                  {'type': 'roundrobin'})
        self.driver.create_server_farm(sf, predictor)

    def test_create_server_farm_with_leastconnections(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_connections = get_fake_predictor('testPredictor01',
                                        {'type': 'leastconnections'})
        self.driver.create_server_farm(sf, predictor_connections)

    def test_create_server_farm_with_hashaddr(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashaddr = get_fake_predictor('testPredictor01',
                                             {'type': 'hashaddr'})
        self.driver.create_server_farm(sf, predictor_hashaddr)

    def test_create_server_farm_with_hashurl(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashurl = get_fake_predictor('testPredictor01',
                                             {'type': 'hashurl'})
        self.driver.create_server_farm(sf, predictor_hashurl)

    def test_delete_server_farm(self):
        sf = get_fake_server_farm('SF-001', {})
        self.driver.delete_server_farm(sf)

    def test_add_real_server_to_server_farm(self):
        sf = get_fake_server_farm('sf-153', {})
        rs = get_fake_rserver('real_server205', {'port': '23'})
        self.driver.add_real_server_to_server_farm(sf, rs)

    def test_delete_real_server_from_server_farm(self):
        sf = get_fake_server_farm('sf-15', {})
        rs = get_fake_rserver('real_server2', {'port': 1122})
        self.driver.delete_real_server_from_server_farm(sf, rs)

    def test_create_virtual_ip(self):
        virtualserver = get_fake_virtual_ip('test', {})
        server_farm = get_fake_server_farm('sf-120', {})
        self.driver.create_virtual_ip(virtualserver, server_farm)

    def test_delete_virtual_ip(self):
        virtualserver = get_fake_virtual_ip('test', {})
        self.driver.delete_virtual_ip(virtualserver)

if __name__ == "__main__":
    unittest.main()
