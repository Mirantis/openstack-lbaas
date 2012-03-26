# -*- coding: utf-8 -*-

from balancer.drivers.haproxy.HaproxyDriver import  HaproxyConfigFile
from balancer.drivers.haproxy.HaproxyDriver import  HaproxyFronted
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
        
    def test_FileName(self):
        filename = HaproxyConfigFile("/tmp/haproxy.cfg", './balancer/tests/unit/testfiles/haproxy.cfg')
        self.assertEqual(filename.GetHAproxyConfigFileName(),  "/tmp/haproxy.cfg")
    def test_DeleteListenBlock (self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg", './balancer/tests/unit/testfiles/haproxy.cfg')
        test.DeleteListenBlock("appli2-insert")
        self.assertTrue(filecmp.cmp("/tmp/haproxy.cfg", "./balancer/tests/unit/testfiles/haproxy_without_appli2-insert.cfg"))
    def test_Temp(self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg", './balancer/tests/unit/testfiles/haproxy.cfg')
        test.AddFronted(self.frontend)
        self.assertTrue(True)
 

if __name__ == "__main__":
	unittest.main()
