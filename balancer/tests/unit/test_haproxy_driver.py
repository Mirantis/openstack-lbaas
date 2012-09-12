# -*- coding: utf-8 -*-

import unittest
#import os
#import shutil
#import filecmp
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
    # this function split dicts with parameters for all objects
    result = dict1
    for i in dict2:
        result[i] = dict2[i]
    return result


def get_fake_rserver(id_, parameters):
    rserver = {'id': id_, 'weight': '8', 'address': '10.2.1.2', \
               'port': '4055'}
    rserver['extra'] = {'minCon': '100', 'maxCon': '2000'}
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
        mock_for_ssh = Mock()
        mock_for_ssh.exec_command.return_value = \
           [MagicMock(spec=file), MagicMock(spec=file), MagicMock(spec=file)]
        self.remote_socket = RemoteControl.RemoteSocketOperation(device_fake)
        self.remote_socket.ssh = mock_for_ssh
        self.driver = Driver.HaproxyDriver(conf, device_fake)
        self.driver.remote_socket.ssh = mock_for_ssh

    def test_get_statistics(self):
        sf = get_fake_server_farm('sf-01', {})
        rs = get_fake_server_farm('real_server1', {'port': 950})
        self.assertTrue(self.remote_socket.\
                        get_statistics(self.driver.remote_socket, sf, rs))


class TestHaproxyDriverAllFunctions(unittest.TestCase):
    def setUp(self):
        # specific Mock object for SSH.
        mock_for_ssh = Mock()
        mock_for_ssh.exec_command.return_value = \
           [MagicMock(spec=file), MagicMock(spec=file), MagicMock(spec=file)]
        self.driver = Driver.HaproxyDriver(conf, device_fake)
        self.driver.remote_config.ssh = mock_for_ssh
        self.driver.remote_socket.ssh = mock_for_ssh
        self.driver.remote_interface.ssh = mock_for_ssh

    def test_create_real_server(self):
        # check implementation of this method in HAProxy driver
        ha_rserver = get_fake_Haproxy_rserver('Test_Rserver')
        self.assertTrue(self.driver.create_real_server(ha_rserver) == None)

    def test_delete_real_server(self):
        # check implementation of this method in HAProxy driver
        ha_rserver = get_fake_Haproxy_rserver('test01')
        self.assertTrue(self.driver.delete_real_server(ha_rserver) == None)

    def test_suspend_real_server(self):
        k = self.driver.remote_config.ssh.exec_command.called
        server_farm = get_fake_server_farm('sf-01', {})
        rserver = get_fake_server_farm('real_server1', {'port': 950})
        self.driver.suspend_real_server(server_farm, rserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_activate_real_server(self):
        k = self.driver.remote_config.ssh.exec_command.called
        server_farm = get_fake_server_farm('sf-02', {})
        rserver = get_fake_server_farm('real_server2', {'maxCon': 40000})
        self.driver.activate_real_server(server_farm, rserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_probe(self):
        # check implementation of this method in HAProxy driver
        probe = get_fake_probe('test-0002', {})
        self.assertTrue(self.driver.create_probe(probe) == None)

    def test_delete_probe(self):
        # check implementation of this method in HAProxy driver
        probe_tcp = get_fake_probe('test-0002', {})
        self.assertTrue(self.driver.delete_probe(probe_tcp) == None)

    def test_add_tcp_probe_to_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        probe = get_fake_probe('test-00344', {'type': 'tcp'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_add_http_probe_to_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        probe = get_fake_probe('test-00344', {'type': 'http'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_add_https_probe_to_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        probe = get_fake_probe('test-00234', {'type': 'https'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_delete_http_probe_from_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        probe = get_fake_probe('test-0002', {'type': 'http'})
        sf = get_fake_server_farm('sf-006', {})
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_delete_https_probe_from_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        probe = get_fake_probe('Test-003', {'type': 'https'})
        sf = get_fake_server_farm('sf-006', {})
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_server_farm_with_round_robin(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('SF-001', {})
        predictor = get_fake_predictor('testPredictor01',
                                  {'type': 'roundrobin'})
        self.driver.create_server_farm(sf, predictor)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_server_farm_with_leastconnections(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('SF-001', {})
        predictor_connections = get_fake_predictor('testPredictor01',
                                        {'type': 'leastconnections'})
        self.driver.create_server_farm(sf, predictor_connections)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_server_farm_with_hashaddr(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashaddr = get_fake_predictor('testPredictor01',
                                             {'type': 'hashaddr'})
        self.driver.create_server_farm(sf, predictor_hashaddr)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_server_farm_with_hashurl(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashurl = get_fake_predictor('testPredictor01',
                                             {'type': 'hashurl'})
        self.driver.create_server_farm(sf, predictor_hashurl)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_delete_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('SF-001', {})
        self.driver.delete_server_farm(sf)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_add_real_server_to_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('sf-153', {})
        rs = get_fake_rserver('real_server205', {'port': '23'})
        self.driver.add_real_server_to_server_farm(sf, rs)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_delete_real_server_from_server_farm(self):
        k = self.driver.remote_config.ssh.exec_command.called
        sf = get_fake_server_farm('sf-15', {})
        rs = get_fake_rserver('real_server2', {'port': 1122})
        self.driver.delete_real_server_from_server_farm(sf, rs)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_create_virtual_ip(self):
        k = self.driver.remote_config.ssh.exec_command.called
        virtualserver = get_fake_virtual_ip('test', {})
        server_farm = get_fake_server_farm('sf-120', {})
        self.driver.create_virtual_ip(virtualserver, server_farm)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_delete_virtual_ip(self):
        k = self.driver.remote_config.ssh.exec_command.called
        virtualserver = get_fake_virtual_ip('test', {})
        self.driver.delete_virtual_ip(virtualserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.remote_config.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

    def test_get_statistics(self):
        k = self.driver.remote_socket.ssh.exec_command.called
        sf = get_fake_server_farm('sf-153', {})
        self.driver.get_statistics(sf)
        self.assertTrue(self.driver.remote_socket.ssh.\
                        exec_command.called > k, 'Error in work with ssh')

if __name__ == "__main__":
    unittest.main()
