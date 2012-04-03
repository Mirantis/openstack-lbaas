# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import filecmp

from balancer.drivers.haproxy.HaproxyDriver import  HaproxyConfigFile
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyFronted
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyBackend
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyRserver
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyListen
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyDriver
from balancer.drivers.haproxy.Context import  Context
from balancer.drivers.haproxy.RemoteControl import RemoteConfig
from balancer.drivers.haproxy.RemoteControl import RemoteService
from balancer.drivers.haproxy.RemoteControl import RemoteInterface
from balancer.drivers.haproxy.RemoteControl import RemoteSocketOperation
from balancer.loadbalancers.serverfarm import ServerFarm
from balancer.loadbalancers.virtualserver import VirtualServer
from balancer.loadbalancers.realserver import RealServer




class HAproxyDriverTestCase (unittest.TestCase):

    def setUp (self):
        #shutil.copyfile ('./balancer/tests/unit/testfiles/haproxy.cfg',  "/tmp/haproxy.cfg")
        self.context = Context()
        self.context.ip = '192.168.19.86'
        self.context.login = 'user'
        self.context.password = 'swordfish'
        self.context.interface = 'eth0'
        self.context.remotepath = '/etc/haproxy'
        self.context.remotename = 'haproxy.cfg'
        #
        self.frontend = HaproxyFronted()
        self.frontend.bind_address='1.1.1.1'
        self.frontend.bind_port='8080'
        self.frontend.default_backend='server_farm'
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
        self.server_farm = ServerFarm()
        self.server_farm.name = 'SFname'
        #
        self.virtualserver = VirtualServer()
        self.virtualserver.name = 'VirtualServer'
        self.virtualserver.address = '115.115.115.115'
        self.virtualserver.port = '8080'
        #
        self.rserver = RealServer()
        self.rserver.name = 'test_real_server'
        self.rserver.address = '123.123.123.123'
        self.rserver.port = '9090'
        self.rserver.weight = '8'
        self.rserver.maxCon = 30000
        #
    def test_IPaddressAdd(self):
        interface = RemoteInterface(self.context,  self.frontend)
        interface.addIP()
        self.assertTrue(True)
    def test_IPaddressDelete(self):
        interface = RemoteInterface(self.context,  self.frontend)
        interface.delIP()
        self.assertTrue(True)   
    def test_suspendRemoteServerViaSocket(self):
        remote_socket = RemoteSocketOperation(self.context,  self.backend,  self.haproxy_rserver)
        remote_socket.suspendServer()
        self.assertTrue(True) 
    def test_activateRemoteServerViaSocket(self):
        remote_socket = RemoteSocketOperation(self.context,  self.backend,  self.haproxy_rserver)
        remote_socket.activateServer()
        self.assertTrue(True) 
    def test_disableRemoteServerInConfig(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.EnableDisableRserverInBackendBlock(self.backend,  self.haproxy_rserver, 'disable')
        self.assertTrue(True) 
    def test_enableRemoteServerInConfig(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.EnableDisableRserverInBackendBlock(self.backend,  self.haproxy_rserver,  'enable')
        self.assertTrue(True) 
    def test_suspendRServer(self):
        driver = HaproxyDriver()
        driver.suspendRServer(self.context,  self.server_farm,  self.rserver)
        self.assertTrue(True)
    def test_activateRServer(self):
        driver = HaproxyDriver()
        driver.activateRServer(self.context,  self.server_farm,  self.rserver)
        self.assertTrue(True)
#    def test_FileName(self):
#        filename = HaproxyConfigFile("/tmp/haproxy.cfg")
#        self.assertEqual(filename.GetHAproxyConfigFileName(),  "/tmp/haproxy.cfg")
#    def test_AddFrontend(self):
#        test = HaproxyConfigFile("/tmp/haproxy.cfg")
#        test.AddFronted(self.frontend)
#        self.assertTrue(True)
#    def test_AddBackend(self):
#        test = HaproxyConfigFile("/tmp/haproxy.cfg")
#        test.AddBackend(self.backend)
#        self.assertTrue(True)
#    def test_DeleteBlock(self):
#        test = HaproxyConfigFile("/tmp/haproxy.cfg")
#        test.DeleteBlock(self.block_for_delete)
#        self.assertTrue(True)
#    def test_AddRserverToBackendBlock(self):
#        test = HaproxyConfigFile("/tmp/haproxy.cfg")
#        test.AddRserverToBackendBlock(self.backend,  self.haproxy_rserver)
#        test.AddRserverToBackendBlock(self.backend,  self.haproxy_rserver1)
#        self.assertTrue(True)
#    def test_DelRserverFromBackendBlock(self):
#        test = HaproxyConfigFile("/tmp/haproxy.cfg")
#        test.DelRserverFromBackendBlock(self.backend,  self.haproxy_rserver)
#        self.assertTrue(True)    
#    def test_createServerFarm(self):
#        driver = HaproxyDriver()
#        driver.createServerFarm(self.context,  self.server_farm)
#        self.assertTrue(True)
#    def test_deleteServerFarm(self):
#        driver = HaproxyDriver()
#        driver.deleteServerFarm(self.context,  self.server_farm)
#        self.assertTrue(True)    
#    def test_createVirtualServer(self):
#        driver = HaproxyDriver()
#        driver.createVIP(self.context,  self.virtualserver,  self.server_farm)
#        self.assertTrue(True)
#    def test_deleteVirtualServer(self):
#        driver = HaproxyDriver()
#        driver.deleteVIP(self.context,  self.virtualserver,   self.server_farm)
#        self.assertTrue(True)
#    def test_addRServerToSF(self):
#        driver = HaproxyDriver()
#        driver.addRServerToSF(self.context,  self.server_farm,  self.rserver)
#        self.assertTrue(True)
#    def test_deleteRServerFromSF(self):
#        driver = HaproxyDriver()
#        driver.deleteRServerFromSF (self.context,  self.server_farm,  self.rserver)
#        self.assertTrue(True)
    def test_checkRemoteHaproxyConfig(self):
        remote_config = RemoteConfig(self.context)
        self.assertTrue(remote_config.validationConfig())

    
    

if __name__ == "__main__":
	unittest.main()
