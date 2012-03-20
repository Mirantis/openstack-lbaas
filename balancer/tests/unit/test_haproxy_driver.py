# -*- coding: utf-8 -*-

from balancer.haproxy_driver.haproxy_config_file_editor import  HaproxyConfigFile
import unittest


class HAproxyDriverTestCase (unittest.TestCase):


    def test_FileName(self):
        filename = HaproxyConfigFile()
        self.assertEqual(filename.GetHAproxyConfigFileName(),  "/etc/haproxy/haproxy.cfg")
      
    def test_DeleteListenBlock (self):
        test = HaproxyConfigFile()
        self.assertEqual(test.DeleteListenBlock("appli1-rewrite"), 'appli1-rewrite')
        



if __name__ == "__main__":
	unittest.main()
