import unittest
import requests
import json
import paramiko
import re

config = {'host': '127.0.0.1', 'port': 8181}

config_create_device = {
    "name": "HAP-001",
    "type": "HAPROXY",
    "version": "1",
    "supports_ipv6": 0,
    "requires_vip_ip": 1,
    "has_acl": 1,
    "supports_vlan": 1,
    "ip": '192.168.19.245',
    "port": "22",
    "user": "user",
    "password": "swordfish",
    "capabilities": {"algorithms": "RoundRobin"}
}

config_create_lb = {
    "device_id": "a854586622ea4282a705e7b1ee833409",
    "name": "testLB001",
    "protocol": "HTTP",
    "transport": "TCP",
    "algorithm": "RoundRobin",
    "virtualIps": [
            {
            "address": "0.0.0.0",
            "mask": "255.255.255.255",
            "type": "PUBLIC",
            "ipVersion": "IPv4",
            "port": "80",
            "ICMPreply": "True"
        }
    ],
    "nodes": [
            {
            "address": "127.0.0.1",
            "type": "host",
            "port": "8001",
            "weight": "1",
            "minCon": "100",
            "maxCon": "1000",
            "rateBandwidth": "12",
            "rateConnection": "1000",
            "status": "INSERVICE",
            "condition": "ENABLED",
            "vm_instance": "RServer001",
            "vm_id": "0001-0001-0001-0001"
        },
            {
            "address": "127.0.0.1",
            "type": "host",
            "port": "8002",
            "weight": "1",
            "minCon": "300",
            "maxCon": "400",
            "rateBandwidth": "12",
            "rateConnection": "1000",
            "status": "INSERVICE",
            "condition": "ENABLED",
            "vm_instance": "RServer002",
            "vm_id": "0002-0002-0002-0002"
        },
            {
            "address": "127.0.0.1",
            "type": "host",
            "port": "8003",
            "weight": "1",
            "minCon": "300",
            "maxCon": "400",
            "rateBandwidth": "12",
            "rateConnection": "1000",
            "status": "INSERVICE",
            "condition": "ENABLED",
            "vm_instance": "RServer003",
            "vm_id": "0003-0003-0003-0003"
        }
    ],
    "healthMonitor": [
            {
            "type": "ICMP",
            "delay": "15",
            "attemptsBeforeDeactivation": "6",
            "timeout": "20"
        },
            {
            "type": "HTTP",
            "delay": "30",
            "attemptsBeforeDeactivation": "5",
            "timeout": "30",
            "method": "GET",
            "path": "/",
            "expected": "200-204"
        }
    ]
}


class TestCreateLB(unittest.TestCase):
    def setUp(self):
        self.remotepath = '/etc/haproxy'
        self.configfilename = 'haproxy.cfg'
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _send_command(self, uri, command):
        try:
            url = 'http://{0}:{1}/{2}'.format(config['host'], config['port'],
                uri)
            r = requests.post(url,
                data=json.dumps(command),
                headers={'Content-Type': 'application/json'})
        except requests.ConnectionError as e:
            self.fail(e.message)
        self.assertIsNone(r.error, 'HTTP error occurred %s' % r.error)
        return r.json

    def _read_haproxy_config(self):
        self.ssh.connect(config_create_device['ip'],
            int(config_create_device['port']),
            config_create_device['user'], config_create_device['password'])
        sftp = self.ssh.open_sftp()
        haproxy_config_file_path = '/tmp/haproxy.cfg.integration_test'
        sftp.get('%s/%s' % (self.remotepath, self.configfilename),
            haproxy_config_file_path)
        sftp.close()
        self.ssh.close()

        haproxy_config_file = open(haproxy_config_file_path, 'r')
        data = haproxy_config_file.read()
        haproxy_config_file.close()

        return data

    def test_create_lb(self):
        response_device = self._send_command('loadbalancers',
            config_create_device)

        self.assertTrue('loadbalancer' in response_device,
            'Response should contain loadbalance key')

        device_id = response_device['loadbalancer']['id']
        self.assertIsNotNone(device_id, 'device_id shouldn\'t be empty')

        lb_config = config_create_lb
        lb_config['device_id'] = device_id

        response_lb = self._send_command('loadbalancers', lb_config)

        self.assertTrue('loadbalancer' in response_device,
            'Response should contain loadbalance key')

        lb_id = response_lb['loadbalancer']['id']
        self.assertIsNotNone(lb_id, 'lb_id shouldn\'t be empty')

        # validate haproxy config
        haproxy_config = self._read_haproxy_config()

        regex_backend = re.compile('backend [0-9a-f]{32}\\b', re.M)
        self.assertIsNotNone(regex_backend.search(haproxy_config),
            'backend section is missing')

        regex_rserver = re.compile(
            'server [0-9a-f]{32} ([\\w.:]+) check maxconn \\d+ inter \\d+')
        rservers = regex_rserver.findall(haproxy_config)
        self.assertIsNotNone(rservers)
        self.assertEqual(3, len(rservers))

        for i in range(0, 2):
            address_ = config_create_lb['nodes'][i]['address'] + ':' +\
                       config_create_lb['nodes'][i]['port']
            self.assertTrue(address_ in rservers)

        # check that remote haproxy is up and service is available
        try:
            url = 'http://{0}:{1}/'.format(
                config_create_lb['virtualIps'][0]['address'],
                config_create_lb['virtualIps'][0]['port'])
            response = requests.get(url)
        except requests.ConnectionError as e:
            self.fail(e.message)
        self.assertIsNone(response.error,
            'HTTP error occurred %s' % response.error)
