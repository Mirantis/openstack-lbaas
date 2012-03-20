# -*- coding: utf-8 -*-

from haproxy_config_file_editor import  HaproxyConfigFile
import unittest


class test_haproxy_config_file_editor (unittest.TestCase):
    def setUp(self):
        pass

    def testFileName(self):
        filename = HaproxyConfigFile()
        print filename.GetFilename()
        self.assertEqual(filename.GetFilename(),  "bla-bla")
      
    

if __name__ == "__main__":
	unittest.main()
