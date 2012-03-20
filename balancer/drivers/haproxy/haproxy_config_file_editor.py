# -*- coding: utf-8 -*-


import re
import sys
import os
from balancer.loadbalancers.realserver import RealServer

#class HaproxyRServer(VServerName):
#   def _init_(self):
#        
#   def AddHaproxyRServer(self):
#        
#        
#    def DeleteHaproxyRServer(self):
#
#class HaproxyVServer:
#    def _init_(self):
#        
#    def CreateHaproxyVServer(self):
    
    
class HaproxyConfigFile:


    def __init__(self):
        self.haproxy_config_file_path = "/etc/haproxy/haproxy.cfg"
        self.haproxy_config_file_tmp_path="/tmp/haproxy.cfg"
        self.debug = False
         
    def GetHAproxyConfigFileName(self):
        return self.haproxy_config_file_path
    
    def DeleteListenBlock (self,  ListenBlockName):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        block_start=False
        new_config_file = []
        #print ListenBlockName
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            if  line.find ('#') >= 0: continue
            if line.find('listen' ) == 0 and  line.find(ListenBlockName) > 0:
                block_start = True
                continue
            elif line.find('listen' ) == -1 and block_start == True:
                continue
            elif  line.find('listen' ) == 0 and block_start == True:
                block_start = False
            new_config_file.append(line.rstrip())
            #print  line.rstrip()
        self.haproxy_config_file.close()
        self.haproxy_config_file_tmp  = open (self.haproxy_config_file_tmp_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file_tmp.write("%s\n" % out_line)
        self.haproxy_config_file_tmp.close()
        return ListenBlockName
 
    def DeleteRServer (self, ListenBlockName, RServerName):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        block_start=False
        new_config_file = []
        for line in  self.haproxy_config_file :
            print line.find(RServerName),  line.find('server'),  block_start
            if  not line.strip(): continue
            if  line.find ('#') >= 0: continue
            if line.find('listen' ) == 0 and  line.find(ListenBlockName) > 0:
                block_start = True
                new_config_file.append(line.rstrip())
                continue
            elif line.find('server') >= 0 and block_start == True and line.find(RServerName) > 0:
                print "bingo"
                continue
            elif  line.find('listen' ) == 0 and block_start == True:
                block_start = False
            new_config_file.append(line.rstrip())
            #print  line.rstrip()
        self.haproxy_config_file.close()
        self.haproxy_config_file_tmp  = open (self.haproxy_config_file_tmp_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file_tmp.write("%s\n" % out_line)
        self.haproxy_config_file_tmp.close()
        return ListenBlockName

        
        
    #def CreateVIP(self, name,  ip, port,  mode,  balance,  option,  reservers):
        
    
    


    
 
if __name__ == '__main__':
    config = HaproxyConfigFile()
    #config.DeleteListenBlock("appli1-rewrite")
    config.DeleteRServer("appli1-rewrite", "app1_2" )
    
    
    
