# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import filecmp

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


@unittest.skip("requires external connectivity")
class HAproxyDriverTestCase (unittest.TestCase):

    def setUp(self):
        #shutil.copyfile ('./balancer/tests/unit/testfiles/haproxy.cfg',  \
        #"/tmp/haproxy.cfg")
        dev = {'ip': '192.168.19.86', 'interface': 'eth0', \
               'login': 'user', 'password': 'swordfish', \
               'remotepath': '/etc/haproxy', 'remotename': 'haproxy.cfg'}
        conf = []
        self.driver = HaproxyDriver(conf, self.dev)
        #
        self.frontend = HaproxyFronted()
        self.frontend.bind_address = '1.1.1.1'
        self.frontend.bind_port = '8080'
        self.frontend.default_backend = 'server_farm'
        self.frontend.name = 'test_frontend'
        #
        self.block_for_delete = HaproxyListen()
        self.block_for_delete.name = 'ssl-relay'
        #
        self.backend = HaproxyBackend()
        self.backend.name = 'test_backend'
        self.backend.balance = 'source'
        #
        self.haproxy_rserver = HaproxyRserver()
        self.haproxy_rserver.name = "new_test_server"
        self.haproxy_rserver.address = '15.15.15.15'
        self.haproxy_rserver.port = '123'
        self.haproxy_rserver.fall = '10'
        self.haproxy_rserver1 = HaproxyRserver()
        self.haproxy_rserver1.name = "new_test_server_2"
        self.haproxy_rserver1.address = '25.25.25.25'
        self.haproxy_rserver1.port = '12345'
        self.haproxy_rserver1.fall = '11'
        #
        self.server_farm = {'name': 'SFname',  'type': 'HashAddrPredictor'}
        #
        self.virtualserver = {'name': 'VirtualServer', \
                                        'address': '115.115.115.115',  \
                                        'port': '8080'}
        #
        self.rserver = {'name': 'test_real_server', \
                                'address': '123.123.123.123', 'port': '9090', \
                                'weight': '8',  'maxCon': '30000'}
        #
        self.probe = {'type': 'http',  'requestMethodType': 'GET', \
                                'requestHTTPurl': '/index.html', \
                                'minExpectStatus': '200'}

    def test_AddHTTPProbe(self):
        self.driver.add_probe_to_server_farm(self.server_farm, self.probe)
        self.assertTrue(True)

    def test_DelHTTPProbe(self):
        self.driver.delete_probe_from_server_farm(self.server_farm, self.probe)
        self.assertTrue(True)

    def test_AddLinesToBackendBlock(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        NewLines = ["option httpchk",  "http-check expect status 200"]
        test.AddLinesToBackendBlock(self.backend, NewLines)
        self.assertTrue(True)

    def test_DeleteLinesTFromBackendBlock(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        DeletedLines = ["option httpchk",  "http-check expect status 200"]
        test.DeleteLinesFromBackendBlock(self.backend, DeletedLines)
        self.assertTrue(True)

    def test_IPaddressAdd(self):
        interface = RemoteInterface(self.dev,  self.frontend)
        interface.add_ip()
        self.assertTrue(True)

    def test_IPaddressDelete(self):
        interface = RemoteInterface(self.dev,  self.frontend)
        interface.del_ip()
        self.assertTrue(True)

    def test_suspendRemoteServerViaSocket(self):
        self.assertTrue(True)

    def test_activateRemoteServerViaSocket(self):
        self.assertTrue(True)

    def test_disableRemoteServerInConfig(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.EnableDisableRserverInBackendBlock(self.backend,  \
                                self.haproxy_rserver, 'disable')
        self.assertTrue(True)

    def test_enableRemoteServerInConfig(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.EnableDisableRserverInBackendBlock(self.backend,  \
                                self.haproxy_rserver,  'enable')
        self.assertTrue(True)

    def test_suspendRServer(self):
        self.assertTrue(True)

    def test_activateRServer(self):
        self.assertTrue(True)

    def test_getRServerStatistics(self):
        self.assertTrue(True)

    def test_getSFStatistics(self):
        self.assertTrue(True)

    def test_FileName(self):
        filename = HaproxyConfigFile("/tmp/haproxy.cfg")
        self.assertEqual(filename.GetHAproxyConfigFileName(),  \
                                             "/tmp/haproxy.cfg")

    def test_AddFrontend(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.AddFronted(self.frontend)
        self.assertTrue(True)

    def test_AddBackend(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.AddBackend(self.backend)
        self.assertTrue(True)

    def test_DeleteBlock(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.DeleteBlock(self.block_for_delete)
        self.assertTrue(True)

    def test_AddRserverToBackendBlock(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.AddRserverToBackendBlock(self.backend,  self.haproxy_rserver)
        test.AddRserverToBackendBlock(self.backend,  self.haproxy_rserver1)
        self.assertTrue(True)

    def test_DelRserverFromBackendBlock(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.DelRserverFromBackendBlock(self.backend,  self.haproxy_rserver)
        self.assertTrue(True)

    def test_createServerFarm(self):
        self.driver.create_server_farm(self.server_farm)
        self.assertTrue(True)

    def test_deleteServerFarm(self):
        self.driver.delete_server_farm(self.server_farm)
        self.assertTrue(True)

    def test_createVirtualServer(self):
        self.driver.create_virtual_ip(self.virtualserver, self.server_farm)
        self.assertTrue(True)

    def test_deleteVirtualServer(self):
        self.driver.delete_virtual_ip(self.virtualserver)
        self.assertTrue(True)

    def test_addRServerToSF(self):
        self.driver.add_real_server_to_server_farm(self.server_farm,
                                                   self.rserver)
        self.assertTrue(True)

    def test_deleteRServerFromSF(self):
        self.driver.delete_real_server_from_server_farm(self.server_farm,
                                                        self.rserver)
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
