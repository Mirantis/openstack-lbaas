# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License

import re
import sys
import os
import shutil
from balancer.loadbalancers.loadbalancer import *
from openstack.common import exception
from balancer.devices.device import LBDevice
from balancer.core.configuration import Configuration
from balancer.loadbalancers.probe import *
from balancer.loadbalancers.realserver import RealServer 
logger = logging.getLogger(__name__)

  
class HaproxyConfigFile:
    def __init__(self, haproxy_config_file_path = '/tmp/haproxy.cfg',  test_config='./balancer/tests/unit/testfiles/haproxy.cfg'):
        shutil.copyfile (test_config, "/tmp/haproxy.cfg")
        self.haproxy_config_file_path = haproxy_config_file_path
    def GetHAproxyConfigFileName(self):
        return self.haproxy_config_file_path
    def DeleteListenBlock (self,  ListenBlockName):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        block_start=False
        new_config_file = []
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            if line.find('listen' ) == 0 and  line.find(ListenBlockName) > 0:
                block_start = True
                logger.debug("Block starting = %s" % block_start)
                continue
            elif line.find('listen' ) == -1 and block_start == True:
                continue
            elif  line.find('listen' ) == 0 and block_start == True:
                block_start = False
            new_config_file.append(line.rstrip())
        self.haproxy_config_file.close()
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file.write("%s\n" % out_line)
        self.haproxy_config_file.close()
        return ListenBlockName
 
    def DeleteRServer (self, ListenBlockName, RServerName):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        block_start=False
        new_config_file = []
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            if line.find('listen' ) == 0 and  line.find(ListenBlockName) > 0:
                block_start = True
                new_config_file.append(line.rstrip())
                continue
            elif line.find('server') >= 0 and block_start == True and line.find(RServerName) > 0:
                continue
            elif  line.find('listen' ) == 0 and block_start == True:
                block_start = False
            new_config_file.append(line.rstrip())
            #print  line.rstrip()
        self.haproxy_config_file.close()
        self.haproxy_config_file  = open (self.haproxy_config_file_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file.write("%s\n" % out_line)
        self.haproxy_config_file.close()
        return ListenBlockName
    
    def AddRServer (self,  ListenBlockName, RServerName, RServerIP,  RServerPort):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        block_start=False
        new_config_file = []
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            if line.find('listen' ) == 0 and  line.find(ListenBlockName) > 0:
                block_start = True
                new_config_file.append(line.rstrip())
                continue
            elif  line.find('listen' ) == 0 and block_start == True:
                new_config_file.append("\tserver\t%s %s:%s check inter 2000 rise 2 fall 5" % (RServerName, RServerIP,  RServerPort) )
                block_start = False
            new_config_file.append(line.rstrip())
            #print  line.rstrip()
        self.haproxy_config_file.close()
        self.haproxy_config_file  = open (self.haproxy_config_file_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file.write("%s\n" % out_line)
        self.haproxy_config_file.close()
        return ListenBlockName       
        
    def AddListenBlock(self,  ListenBlockName,  VIPServerIP,  VIPServerPort):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        new_config_file = []
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            new_config_file.append(line.rstrip())
        self.haproxy_config_file.close()
        new_config_file.append("listen %s %s:%s" % (ListenBlockName, VIPServerIP,  VIPServerPort))
        new_config_file.append("\tmode http")
        new_config_file.append("\tbalance roundrobin")
        new_config_file.append("\toption httpclose")
        self.haproxy_config_file  = open (self.haproxy_config_file_path,  "w")
        for out_line in new_config_file:
            self.haproxy_config_file.write("%s\n" % out_line)
        self.haproxy_config_file.close()
        return ListenBlockName

if __name__ == '__main__':
    config = HaproxyConfigFile('/tmp/haproxy.cfg', '../../tests/unit/testfiles/haproxy.cfg')
    config.DeleteListenBlock("appli2-insert")
    #config.DeleteRServer("appli1-rewrite", "app1_2" )
    #config.AddRServer("appli1-rewrite", "new_server", "1.1.1.1", "80"  )
    #config.AddListenBlock("new_block", "12.12.12.12", "80" )
    
    
    
    
