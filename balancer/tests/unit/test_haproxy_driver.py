# -*- coding: utf-8 -*-

import unittest
import paramiko
from mock import Mock, MagicMock, patch

import balancer.drivers.haproxy.haproxy_driver as Driver
import balancer.drivers.haproxy.remote_control as RemoteControl

device_fake = {'id': 'fake1',
               'type': 'FAKE',
               'version': '1',
               'ip': '10.0.0.10',
               'port': 1010,
               'user': 'user1',
               'password': 'secrete1',
               'extra': {'interface': 'eth0',
               'socket': '/tmp/haproxy.sock'}}

conf = []

def init_mock_channel():
    mock_channel = Mock()
    mock_channel.channel.recv_exit_status.return_value = 0
    mock_channel.read.return_value = "fake"
    return mock_channel

def init_ssh_mock():
    mock_for_ssh = Mock()
    mock_channel = init_mock_channel()
    mock_for_ssh.exec_command.return_value = \
         [mock_channel, mock_channel, mock_channel]
    return mock_for_ssh


def init_driver_with_mock():
    mock_for_ssh = init_ssh_mock()
    driver = Driver.HaproxyDriver(conf, device_fake)
    driver._remote_ctrl._ssh = mock_for_ssh
    return driver


def get_fake_rserver(id_, parameters):
    rserver = {'id': id_, 'weight': '8', 'address': '10.2.1.2', \
               'port': '4055'}
    rserver['extra'] = {'minCon': '100', 'maxCon': '2000'}
    rserver.update(parameters)
    return rserver


def get_fake_server_farm(id_, parameters):
    server_farm = {'id': id_, 'type': 'Host'}
    server_farm.update(parameters)
    return server_farm


def get_fake_virtual_ip(id_, parameters):
    vip = {'id': id_, 'address': '100.1.1.1', 'port': '8801'}
    vip.update(parameters)
    return vip


def get_fake_probe(id_, parameters):
    probe = {'id': id_, 'type': 'HTTP', 'requestMethodType': 'GET', \
             'requestHTTPUrl': '/index.html', 'minExpectStatus': '300'}
    probe.update(parameters)
    return probe


def get_fake_predictor(id_, parameters):
    predictor = {'id': id_, 'type': 'roundrobin', 'extra': {}}
    predictor.update(parameters)
    return predictor


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


class TestHaproxyDriverRemoteService(unittest.TestCase):
    def setUp(self):
        self.ssh = init_ssh_mock()
        remote_ctrl = RemoteControl.RemoteControl(device_fake)
        remote_ctrl._ssh = self.ssh
        self.remote_service = RemoteControl.RemoteService(remote_ctrl)

    def test_start_service(self):
        self.remote_service.start()
        self.ssh.exec_command.assert_called_once_with('sudo service haproxy start')

    def test_stop_service(self):
        self.remote_service.stop()
        self.ssh.exec_command.assert_called_once_with('sudo service haproxy stop')

    def test_restart_service(self):
        self.remote_service.restart()
        self.ssh.exec_command.assert_called_once_with('sudo haproxy'
                              ' -f /etc/haproxy/haproxy.cfg'
                              ' -p /var/run/haproxy.pid'
                              ' -sf $(cat /var/run/haproxy.pid)')


class TestHaproxyDriverRemoteInterface(unittest.TestCase):
    def setUp(self):
        self.ssh = init_ssh_mock()
        self.frontend = get_fake_HaproxyFrontend('test')
        remote_ctrl = RemoteControl.RemoteControl(device_fake)
        remote_ctrl._ssh = self.ssh
        self.remote_interface = RemoteControl.RemoteInterface(device_fake,
                                                              remote_ctrl)

    def test_add_ip(self):
        # ip wasn't configured on the interface
        self.assertTrue(self.remote_interface.add_ip(self.frontend))
        self.assertEqual(self.ssh.exec_command.call_count, 2)
        self.assertEqual(self.ssh.exec_command.call_args_list[0][0][0],
                         'ip addr show dev eth0')
        self.assertEqual(self.ssh.exec_command.call_args_list[1][0][0],
                         'sudo ip addr add 1.1.1.1/32 dev eth0')

        # ip was already configured on the interface
        self.ssh.reset_mock()
        mock_channel = init_mock_channel()
        mock_channel.read.return_value = "1.1.1.1"
        self.ssh.exec_command.return_value = [mock_channel, mock_channel,
                                              mock_channel]
        self.assertTrue(self.remote_interface.add_ip(self.frontend))
        self.assertEqual(self.ssh.exec_command.call_count, 1)
        self.assertEqual(self.ssh.exec_command.call_args[0][0],
                         'ip addr show dev eth0')

    def test_del_ip(self):
        # ip wasn't configured on the interface
        self.assertTrue(self.remote_interface.del_ip(self.frontend))
        self.assertEqual(self.ssh.exec_command.call_count, 1)
        self.assertEqual(self.ssh.exec_command.call_args[0][0],
                         'ip addr show dev eth0')

        # ip was already configured on the interface
        self.ssh.reset_mock()
        mock_channel = init_mock_channel()
        mock_channel.read.return_value = "1.1.1.1"
        self.ssh.exec_command.return_value = [mock_channel, mock_channel,
                                              mock_channel]
        self.assertTrue(self.remote_interface.del_ip(self.frontend))
        self.assertEqual(self.ssh.exec_command.call_count, 2)
        self.assertEqual(self.ssh.exec_command.call_args_list[0][0][0],
                         'ip addr show dev eth0')
        self.assertEqual(self.ssh.exec_command.call_args_list[1][0][0],
                         'sudo ip addr del 1.1.1.1/32 dev eth0')


class TestHaproxyDriverRemoteSocketOperation(unittest.TestCase):
    def setUp(self):
        remote_ctrl = RemoteControl.RemoteControl(device_fake)
        self.ssh = init_ssh_mock()
        remote_ctrl._ssh = self.ssh
        self.remote_socket = RemoteControl.RemoteSocketOperation(device_fake,
                                                                 remote_ctrl)
        self.driver = init_driver_with_mock()

    def test_get_statistics(self):
        sf = get_fake_server_farm('sf-01', {})
        self.assertTrue(self.remote_socket.\
                        get_statistics(self.driver.remote_socket, sf))


class TestHaproxyDriverAllFunctions(unittest.TestCase):
    def setUp(self):
        self.driver = init_driver_with_mock()
        open('/tmp/haproxy.cfg', 'w')

    def test_create_real_server(self):
        # check implementation of this method in HAProxy driver
        ha_rserver = get_fake_Haproxy_rserver('Test_Rserver')
        self.assertTrue(self.driver.create_real_server(ha_rserver) == None)

    def test_delete_real_server(self):
        # check implementation of this method in HAProxy driver
        ha_rserver = get_fake_Haproxy_rserver('test01')
        self.assertTrue(self.driver.delete_real_server(ha_rserver) == None)

    def test_suspend_real_server(self):
        server_farm = get_fake_server_farm('sf-01', {})
        rserver = get_fake_rserver('real_server1', {'port': 950})
        self.driver.suspend_real_server(server_farm, rserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_activate_real_server(self):
        server_farm = get_fake_server_farm('sf-02', {})
        rserver = get_fake_rserver('real_server2', {'maxCon': 40000})
        self.driver.activate_real_server(server_farm, rserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_probe(self):
        # check implementation of this method in HAProxy driver
        probe = get_fake_probe('test-0002', {})
        self.assertTrue(self.driver.create_probe(probe) == None)

    def test_delete_probe(self):
        # check implementation of this method in HAProxy driver
        probe_tcp = get_fake_probe('test-0002', {})
        self.assertTrue(self.driver.delete_probe(probe_tcp) == None)

    def test_add_tcp_probe_to_server_farm(self):
        probe = get_fake_probe('test-00344', {'type': 'tcp'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_add_http_probe_to_server_farm(self):
        probe = get_fake_probe('test-00344', {'type': 'http'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_add_https_probe_to_server_farm(self):
        probe = get_fake_probe('test-00234', {'type': 'https'})
        sf = get_fake_server_farm('sf-003', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_delete_http_probe_from_server_farm(self):
        probe = get_fake_probe('test-0002', {'type': 'http'})
        sf = get_fake_server_farm('sf-006', {})
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_delete_https_probe_from_server_farm(self):
        probe = get_fake_probe('Test-003', {'type': 'https'})
        sf = get_fake_server_farm('sf-006', {})
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_server_farm_with_round_robin(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor = get_fake_predictor('testPredictor01',
                                  {'type': 'roundrobin'})
        self.driver.create_server_farm(sf, predictor)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_server_farm_with_leastconnections(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_connections = get_fake_predictor('testPredictor01',
                                        {'type': 'leastconnections'})
        self.driver.create_server_farm(sf, predictor_connections)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_server_farm_with_hashaddr(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashaddr = get_fake_predictor('testPredictor01',
                                             {'type': 'hashaddr'})
        self.driver.create_server_farm(sf, predictor_hashaddr)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_server_farm_with_hashurl(self):
        sf = get_fake_server_farm('SF-001', {})
        predictor_hashurl = get_fake_predictor('testPredictor01',
                                             {'type': 'hashurl'})
        self.driver.create_server_farm(sf, predictor_hashurl)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_delete_server_farm(self):
        sf = get_fake_server_farm('SF-001', {})
        self.driver.delete_server_farm(sf)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_add_real_server_to_server_farm(self):
        sf = get_fake_server_farm('sf-153', {})
        rs = get_fake_rserver('real_server205', {'port': '23'})
        self.driver.add_real_server_to_server_farm(sf, rs)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_delete_real_server_from_server_farm(self):
        sf = get_fake_server_farm('sf-15', {})
        rs = get_fake_rserver('real_server2', {'port': 1122})
        self.driver.delete_real_server_from_server_farm(sf, rs)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_create_virtual_ip(self):
        virtualserver = get_fake_virtual_ip('test', {})
        server_farm = get_fake_server_farm('sf-120', {})
        self.driver.create_virtual_ip(virtualserver, server_farm)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_delete_virtual_ip(self):
        virtualserver = get_fake_virtual_ip('test', {})
        self.driver.delete_virtual_ip(virtualserver)
        self.driver.finalize_config(True)
        self.assertTrue(self.driver.config_manager.remote_control._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

    def test_get_statistics(self):
        sf = get_fake_server_farm('sf-153', {})
        self.driver.get_statistics(sf)
        self.assertTrue(self.driver.remote_socket.remote_ctrl._ssh.\
                        exec_command.called == 1, 'Error in work with ssh')

if __name__ == "__main__":
    unittest.main()
