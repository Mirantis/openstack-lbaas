# -*- coding: utf-8 -*-

import unittest
import os
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

test_config_file = '''global
\tlog 127.0.0.1   local0
\tlog 127.0.0.1   local1 debug
\t#log loghost    local0 info
\tmaxconn 4096
\t#chroot /usr/share/haproxy
\tuser haproxy
\tgroup haproxy
\tdaemon
\t#debug
\t#quiet
\tstats socket /tmp/haproxy.sock user root level admin
defaults
\tlog     global
\tmode    http
\toption  httplog
\toption  dontlognull
\tretries 3
\toption redispatch
\tmaxconn 2000
\tcontimeout      5000
\tclitimeout      50000
\tsrvtimeout      50000
backend test_backend1
\tbalance roundrobin
\toption httpchk GET /
\tserver test_server1 1.1.1.1 check maxconn 10000 inter 2000 rise 2 fall 3
\tserver test_server2 1.1.1.2 check maxconn 10 inter 20 rise 2 fall 3 disabled
frontend test_frontend1
\tbind 192.168.19.245:80
\tmode http
\tdefault_backend 719beee908cf428fa542bc15d929ba18
'''

conf = []


def init_mock_channel():
    mock_channel = Mock()
    mock_channel.channel.recv_exit_status.return_value = 0
    mock_channel.read.return_value = "test"
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
    rserver = {'id': id_, 'weight': 8, 'address': '1.1.1.3',\
               'port': 23, 'condition': 'enabled'}
    rserver['extra'] = {'minconn': 100, 'maxconn': 2000, 'inter': 100,
                        'rise': 3, 'fall': 4}
    rserver.update(parameters)
    return rserver


def get_fake_server_farm(id_, parameters):
    server_farm = {'id': id_, 'type': 'Host'}
    server_farm.update(parameters)
    return server_farm


def get_fake_virtual_ip(id_, parameters):
    vip = {'id': id_, 'address': '100.1.1.1', 'port': '8801',
           'extra': {'protocol': 'tcp'}}
    vip.update(parameters)
    return vip


def get_fake_probe(id_, parameters):
    probe = {'id': id_, 'type': 'HTTP', 'requestMethodType': 'GET', \
             'path': '/test.html', 'minExpectStatus': '300'}
    probe.update(parameters)
    return probe


def get_fake_predictor(id_, parameters):
    predictor = {'id': id_, 'type': 'roundrobin', 'extra': {}}
    predictor.update(parameters)
    return predictor


def get_fake_HaproxyFrontend(id_):
    frontend = Driver.HaproxyFronted({'id': id_, 'address': '1.1.1.1',
                                      'port': '8080'})
    frontend.default_backend = 'server_farm'
    return frontend


def get_fake_HaproxyBackend(id_):
    backend = Driver.HaproxyBackend(id_)
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
        self.ssh.exec_command.assert_called_once_with(
                          'sudo service haproxy start')

    def test_stop_service(self):
        self.remote_service.stop()
        self.ssh.exec_command.assert_called_once_with(
                           'sudo service haproxy stop')

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
        self.ssh = init_ssh_mock()
        remote_ctrl = RemoteControl.RemoteControl(device_fake)
        remote_ctrl._ssh = self.ssh
        self.backend = get_fake_HaproxyBackend('test_backend')
        self.rserver = get_fake_rserver('test_rserver', {})
        self.remote_socket = RemoteControl.RemoteSocketOperation(device_fake,
                                                                 remote_ctrl)
        self.driver = init_driver_with_mock()

    def test_suspend_server(self):
        self.assertTrue(self.remote_socket.suspend_server(self.backend,
                                                          self.rserver))
        self.ssh.exec_command.assert_called_once_with(
                          'echo disable server test_backend/test_rserver | '
                          'sudo socat stdio unix-connect:/tmp/haproxy.sock')

    def test_activate_server(self):
        self.assertTrue(self.remote_socket.activate_server(self.backend,
                                                           self.rserver))
        self.ssh.exec_command.assert_called_once_with(
                          'echo enable server test_backend/test_rserver | '
                          'sudo socat stdio unix-connect:/tmp/haproxy.sock')

    def test_get_statistics(self):
        self.assertTrue(self.remote_socket.get_statistics(self.backend.name,
                                                          self.rserver['id']))
        self.ssh.exec_command.assert_called_once_with(
                          'echo show stat | sudo socat stdio unix-connect:'
                          '/tmp/haproxy.sock | grep test_backend,test_rserver')


class TestHaproxyDriverAllFunctions(unittest.TestCase):
    def setUp(self):
        self.driver = init_driver_with_mock()
        self.ssh = self.driver._remote_ctrl._ssh
        self.config_file_name = '/tmp/haproxy.cfg'
        f = open(self.config_file_name, 'w')
        f.write(test_config_file)
        f.close()

    def tearDown(self):
        if os.path.exists(self.config_file_name):
            os.remove(self.config_file_name)

    def check_line_on_pos(self, line, position):
        lines = open(self.config_file_name).read().splitlines()
        self.assertEqual(line, lines[position])

    def is_line_in_config(self, line):
        lines = open(self.config_file_name).read().splitlines()
        return line in lines

    def test_suspend_real_server(self):
        server_farm = get_fake_server_farm('test_backend1', {})
        rserver = get_fake_rserver('test_server1', {})
        self.check_line_on_pos('\tserver test_server1 1.1.1.1'
                               ' check maxconn 10000 inter 2000 rise 2'
                               ' fall 3',
                               26)
        self.driver.suspend_real_server(server_farm, rserver)
        self.check_line_on_pos('\tserver test_server1 1.1.1.1'
                               ' check maxconn 10000 inter 2000 rise 2'
                               ' fall 3 disabled',
                               26)
        self.ssh.exec_command.assert_called_once_with(
                          'echo disable server test_backend1/test_server1 | '
                          'sudo socat stdio unix-connect:/tmp/haproxy.sock')

    def test_activate_real_server(self):
        server_farm = get_fake_server_farm('test_backend1', {})
        rserver = get_fake_rserver('test_server2', {})
        self.check_line_on_pos('\tserver test_server2 1.1.1.2'
                               ' check maxconn 10 inter 20 rise 2'
                               ' fall 3 disabled',
                               27)
        self.driver.activate_real_server(server_farm, rserver)
        self.check_line_on_pos('\tserver test_server2 1.1.1.2'
                               ' check maxconn 10 inter 20 rise 2'
                               ' fall 3',
                               27)
        self.ssh.exec_command.assert_called_once_with(
                          'echo enable server test_backend1/test_server2 | '
                          'sudo socat stdio unix-connect:/tmp/haproxy.sock')

    def test_add_tcp_probe_to_server_farm(self):
        probe = get_fake_probe('test_probe1', {'type': 'tcp'})
        sf = get_fake_server_farm('test_backend1', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.check_line_on_pos('\toption httpchk', 25)

    def test_add_http_probe_to_server_farm(self):
        probe = get_fake_probe('test_probe1', {'type': 'http'})
        sf = get_fake_server_farm('test_backend1', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.check_line_on_pos('\toption httpchk GET /test.html', 26)

    def test_add_https_probe_to_server_farm(self):
        probe = get_fake_probe('test_probe1', {'type': 'https'})
        sf = get_fake_server_farm('test_backend1', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.check_line_on_pos('\toption ssl-hello-chk', 26)

    def test_delete_http_probe_from_server_farm(self):
        probe = get_fake_probe('test_probe1', {'type': 'http'})
        sf = get_fake_server_farm('test_backend1', {})
        self.assertTrue(self.is_line_in_config('\toption httpchk GET /'))
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.assertFalse(self.is_line_in_config('\toption httpchk GET /'))

    def test_delete_https_probe_from_server_farm(self):
        probe = get_fake_probe('test_probe1', {'type': 'https'})
        sf = get_fake_server_farm('test_backend1', {})
        self.driver.add_probe_to_server_farm(sf, probe)
        self.assertTrue(self.is_line_in_config('\toption ssl-hello-chk'))
        self.driver.delete_probe_from_server_farm(sf, probe)
        self.assertFalse(self.is_line_in_config('\toption ssl-hello-chk'))

    def test_create_server_farm_with_round_robin(self):
        sf = get_fake_server_farm('test_backend2', {})
        predictor = get_fake_predictor('test_predictor1',
                                       {'type': 'round_robin'})
        self.driver.create_server_farm(sf, predictor)
        self.check_line_on_pos('backend test_backend2', 28)
        self.check_line_on_pos('\tbalance roundrobin', 29)

    def test_create_server_farm_with_leastconnections(self):
        sf = get_fake_server_farm('test_backend2', {})
        predictor = get_fake_predictor('test_predictor1',
                                       {'type': 'least_connection'})
        self.driver.create_server_farm(sf, predictor)
        self.check_line_on_pos('backend test_backend2', 28)
        self.check_line_on_pos('\tbalance leastconn', 29)

    def test_create_server_farm_with_hashsource(self):
        sf = get_fake_server_farm('test_backend2', {})
        predictor = get_fake_predictor('test_predictor1',
                                       {'type': 'hash_source'})
        self.driver.create_server_farm(sf, predictor)
        self.check_line_on_pos('backend test_backend2', 28)
        self.check_line_on_pos('\tbalance source', 29)

    def test_create_server_farm_with_hashuri(self):
        sf = get_fake_server_farm('test_backend2', {})
        predictor = get_fake_predictor('test_predictor1',
                                       {'type': 'hash_uri'})
        self.driver.create_server_farm(sf, predictor)
        self.check_line_on_pos('backend test_backend2', 28)
        self.check_line_on_pos('\tbalance uri', 29)

    def test_delete_server_farm(self):
        sf = get_fake_server_farm('test_backend1', {})
        self.assertTrue(self.is_line_in_config('backend test_backend1'))
        self.assertTrue(self.is_line_in_config('\tbalance roundrobin'))
        self.assertTrue(self.is_line_in_config('\toption httpchk GET /'))
        self.assertTrue(self.is_line_in_config('\tserver test_server1 1.1.1.1 '
                                               'check maxconn 10000 inter 2000'
                                               ' rise 2 fall 3'))
        self.assertTrue(self.is_line_in_config('\tserver test_server2 1.1.1.2 '
                                               'check maxconn 10 inter 20 rise'
                                               ' 2 fall 3 disabled'))
        self.driver.delete_server_farm(sf)
        self.assertFalse(self.is_line_in_config('backend test_backend1'))
        self.assertFalse(self.is_line_in_config('\tbalance roundrobin'))
        self.assertFalse(self.is_line_in_config('\toption httpchk GET /'))
        self.assertFalse(self.is_line_in_config('\tserver test_server1 1.1.1.1'
                                                ' check maxconn 10000 inter '
                                                '2000 rise 2 fall 3'))
        self.assertFalse(self.is_line_in_config('\tserver test_server2 1.1.1.2'
                                                ' check maxconn 10 inter 20 '
                                                'rise 2 fall 3 disabled'))

    def test_add_real_server_to_server_farm(self):
        sf = get_fake_server_farm('test_backend1', {})
        rs = get_fake_rserver('test_server3', {'port': '23'})
        self.driver.add_real_server_to_server_farm(sf, rs)
        self.check_line_on_pos('\tserver test_server3 1.1.1.3:23 check maxconn'
                               ' 2000 inter 100 rise 3 fall 4', 28)
        rs['extra']['condition'] = 'disabled'
        self.driver.add_real_server_to_server_farm(sf, rs)
        self.check_line_on_pos('\tserver test_server3 1.1.1.3:23 check maxconn'
                               ' 2000 inter 100 rise 3 fall 4 disabled', 29)

    def test_delete_real_server_from_server_farm(self):
        sf = get_fake_server_farm('test_backend1', {})
        rs = get_fake_rserver('test_server2', {})
        self.assertTrue(self.is_line_in_config('\tserver test_server1 1.1.1.1 '
                                               'check maxconn 10000 inter 2000'
                                               ' rise 2 fall 3'))
        self.assertTrue(self.is_line_in_config('\tserver test_server2 1.1.1.2 '
                                               'check maxconn 10 inter 20 rise'
                                               ' 2 fall 3 disabled'))
        self.driver.delete_real_server_from_server_farm(sf, rs)
        self.assertFalse(self.is_line_in_config('\tserver test_server2 1.1.1.2'
                                               ' check maxconn 10 inter 20'
                                               ' rise 2 fall 3 disabled'))
        self.assertTrue(self.is_line_in_config('\tserver test_server1 1.1.1.1 '
                                               'check maxconn 10000 inter 2000'
                                               ' rise 2 fall 3'))

    def test_create_virtual_ip(self):
        virtualserver = get_fake_virtual_ip('test_frontend2', {})
        server_farm = get_fake_server_farm('test_backend1', {})
        self.driver.create_virtual_ip(virtualserver, server_farm)
        self.check_line_on_pos('frontend test_frontend2', 32)
        self.check_line_on_pos('\tbind 100.1.1.1:8801', 33)
        self.check_line_on_pos('\tdefault_backend test_backend1', 34)
        self.check_line_on_pos('\tmode tcp', 35)

        self.assertEqual(self.ssh.exec_command.call_count, 2)
        self.assertEqual(self.ssh.exec_command.call_args_list[0][0][0],
                         'ip addr show dev eth0')
        self.assertEqual(self.ssh.exec_command.call_args_list[1][0][0],
                         'sudo ip addr add 100.1.1.1/32 dev eth0')

    def test_delete_virtual_ip(self):
        mock_channel = init_mock_channel()
        mock_channel.read.return_value = "...100.1.1.1..."
        self.ssh.exec_command.return_value = [mock_channel, mock_channel,
                                              mock_channel]
        virtualserver = get_fake_virtual_ip('test_frontend1', {})
        self.assertTrue(self.is_line_in_config('frontend test_frontend1'))
        self.assertTrue(self.is_line_in_config('\tbind 192.168.19.245:80'))
        self.assertTrue(self.is_line_in_config(
                        '\tdefault_backend 719beee908cf428fa542bc15d929ba18'))
        self.assertTrue(self.is_line_in_config('\tmode http'))
        self.driver.delete_virtual_ip(virtualserver)
        self.assertFalse(self.is_line_in_config('frontend test_frontend1'))
        self.assertFalse(self.is_line_in_config('\tbind 192.168.19.245:80'))
        self.assertFalse(self.is_line_in_config(
                        '\tdefault_backend 719beee908cf428fa542bc15d929ba18'))
        self.assertFalse(self.is_line_in_config('\tmode http'))

        self.assertEqual(self.ssh.exec_command.call_count, 2)
        self.assertEqual(self.ssh.exec_command.call_args_list[0][0][0],
                         'ip addr show dev eth0')
        self.assertEqual(self.ssh.exec_command.call_args_list[1][0][0],
                         'sudo ip addr del 100.1.1.1/32 dev eth0')

    def test_get_statistics(self):
        stats = '041493dca01344adad9a04b5d9a50ac8,804e181ef8ec427d810ef46f0d'\
        'bd9cb2,0,0,0,1,1000,2,318,572,,0,,0,0,0,0,UP,1,1,0,0,0,1116,0,,1,1,'\
        '1,,2,,2,0,,1,L7OK,200,0,0,2,0,0,0,0,0,,,,0,0,'
        mock_channel = init_mock_channel()
        mock_channel.read.return_value = stats
        self.ssh.exec_command.return_value = [mock_channel, mock_channel,
                                              mock_channel]

        sf = get_fake_server_farm('test_backend1', {})
        rserver = get_fake_rserver('test_server1', {})
        statistics = self.driver.get_statistics(sf, rserver)
        self.assertEqual(statistics, {'connFail': '0', 'weight': '1',
                                      'connCurrent': '0', 'connMax': '1',
                                      'connTotal': '2', 'state': 'UP',
                                      'connRateLimit': '',
                                      'bandwRateLimit': '1'})
        self.ssh.exec_command.assert_called_once_with(
                          'echo show stat | sudo socat stdio unix-connect:/tmp'
                          '/haproxy.sock | grep test_backend1,test_server1')

    def test_finalize_config(self):
        mock_channel = init_mock_channel()
        self.ssh.exec_command.return_value = [mock_channel, mock_channel,
                                              mock_channel]

        self.driver._remote_ctrl.open()
        self.driver.finalize_config(False)
        self.assertFalse(self.ssh.exec_command.called)
        self.assertTrue(self.ssh.close.called)

        # config is valid
        mock_channel.read.return_value = 'Configuration file is valid'
        self.driver.config_manager.need_deploy = True
        self.driver.finalize_config(True)
        self.assertEqual(self.ssh.exec_command.call_count, 3)
        self.assertEqual(self.ssh.exec_command.call_args_list[0][0][0],
                         'haproxy -c -f /tmp/haproxy.cfg.remote')
        self.assertEqual(self.ssh.exec_command.call_args_list[1][0][0],
                         'sudo mv /tmp/haproxy.cfg.remote '
                         '/etc/haproxy/haproxy.cfg')
        self.assertEqual(self.ssh.exec_command.call_args_list[2][0][0],
                         'sudo haproxy -f /etc/haproxy/haproxy.cfg'
                         ' -p /var/run/haproxy.pid -sf '
                         '$(cat /var/run/haproxy.pid)')
        self.assertTrue(self.ssh.close.called)

        # config is invalid
        self.ssh.reset_mock()
        mock_channel.read.return_value = 'ERROR'
        self.driver.config_manager.need_deploy = True
        self.driver.finalize_config(True)
        self.ssh.exec_command.assert_called_once_with(
                        'haproxy -c -f /tmp/haproxy.cfg.remote')
        self.assertTrue(self.ssh.close.called)

    def test_get_capabilities(self):
        capabilities = self.driver.get_capabilities()
        self.assertEqual(capabilities, {'algorithms': ['STATIC_RR',
                                                       'ROUND_ROBIN',
                                                       'HASH_SOURCE',
                                                       'LEAST_CONNECTION',
                                                       'HASH_URI'],
                                        'protocols': ['HTTP', 'TCP']})

if __name__ == "__main__":
    unittest.main()
