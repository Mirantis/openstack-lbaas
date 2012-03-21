# -*- coding: utf-8 -*-

from balancer.drivers.haproxy.haproxy_config_file_editor import  HaproxyConfigFile
import unittest
import os
import shutil
import filecmp


class HAproxyDriverTestCase (unittest.TestCase):
    def setUp (self):
        shutil.copyfile ('./balancer/tests/unit/testfiles/haproxy.cfg',  "/tmp/haproxy.cfg")
        
    def test_FileName(self):
        filename = HaproxyConfigFile("/tmp/haproxy.cfg")
        self.assertEqual(filename.GetHAproxyConfigFileName(),  "/tmp/haproxy.cfg")
    def test_DeleteListenBlock (self):
        test = HaproxyConfigFile("/tmp/haproxy.cfg")
        test.DeleteListenBlock("appli2-insert")
        self.assertTrue(filecmp.cmp("/tmp/haproxy.cfg", "./balancer/tests/unit/testfiles/haproxy_without_appli2-insert.cfg"))
 

if __name__ == "__main__":
	unittest.main()
