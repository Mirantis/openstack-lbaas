# -*- coding: utf-8 -*-

import os

class HaproxyConfigFile():
    def __init__(self,  haproxy_config_file_path):
        self.haproxy_config_file_path = haproxy_config_file_path
        
    
    def get_filename (self):
        return self.haproxy_config_file_path
    
if __name__ == '__main__':
	haproxyconfigfile = ("bla-bla")
	filename = haproxyconfigfile.get_filename()
	print filename
    
