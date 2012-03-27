# -*- coding: utf-8 -*-

from balancer.drivers.haproxy.HaproxyDriver import  HaproxyConfigFile
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyFronted
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyBackend
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyListen
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyDriver
from balancer.loadbalancers.serverfarm import ServerFarm
import unittest
import os
import shutil
import filecmp


class HAproxyDriverTestCase (unittest.TestCase):
    def setUp (self):
        shutil.copyfile ('./balancer/tests/unit/testfiles/haproxy.cfg',  "/tmp/haproxy.cfg")
        self.frontend = HaproxyFronted()
        self.frontend.bind_address='1.1.1.1'
        self.frontend.bind_port='8080'
        self.frontend.default_backend='server_farm'
        self.frontend.name = 'test_frontend'
        self.block_for_delete = HaproxyListen()
        self.block_for_delete.name = 'ssl-relay'
        self.backend = HaproxyBackend()
        self.backend.name = 'test_backend'
        self.backend.balance = 'source'
        
    def test_FileName(self):
        filename = HaproxyConfigFile("/tmp/haproxy.cfg")
        self.assertEqual(filename.GetHAproxyConfigFileName(),  "/tmp/haproxy.cfg")
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
    def test_createServerFarm(self):
        server_farm = ServerFarm
        driver = HaproxyDriver
        driver.createServerFarm(server_farm)
        self.assertTrue(True)
        


if __name__ == "__main__":
	unittest.main()
