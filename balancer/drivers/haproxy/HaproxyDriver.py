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


import sys
import os
import logging


from balancer.drivers.BaseDriver import BaseDriver
#from balancer.drivers.haproxy.Context import Context

logger = logging.getLogger(__name__)

class HaproxyDriver(BaseDriver):
    def __init__(self):
        
        pass

    def createRServer(self, vserver, rserver,  context):
        pass
    
    def deleteRServer(self, vserver,  context, rserver):
        pass
    
    def createVIP(self,  context, vip,  sfarm): 
        pass
    
    def deleteVIP(self,  context,  vip):
        pass

    def createServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            logger.error ("Serverfarm name is empty")
            return "SERVERFARM FARM NAME ERROR"
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm.name
        config_file = HaproxyConfigFile()
        config_file.AddBackend(haproxy_serverfarm)

    def deleteServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            logger.error ("Serverfarm name is empty")
            return "SERVER FARM NAME ERROR"
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm.name
        config_file = HaproxyConfigFile()
        config_file.DeleteBlock(haproxy_serverfarm)       

class HaproxyConfigBlock:
    def __init__(self):
        self.name = ""
        self.type = ""
        
class HaproxyFronted(HaproxyConfigBlock):
    def __init__(self):
        self.type="frontend"
        self.bind_address = ""
        self.bind_port= ""
        self.default_backend = ""
        self.mode = "http"

class HaproxyBackend(HaproxyConfigBlock):
    def __init__(self):
        self.type="backend"
        self.mode = ""
        self.balance = "source"
        
class HaproxyListen(HaproxyConfigBlock):
    def __init__(self):
        self.type="listen"
        self.name = ""
        self.mode = ""
        self.balance = "source"
   
class HaproxyRserver():
    def __init__(self):
        self.name = ""
        self.address = ""
        self.check = False
        self.cookie = ""
        self.disabled = False
        self.error_limit = 10
        self.fall = 0
        self.id = ""
        self.inter = 2000
        self.fastinter = 2000
        self.downinter = 2000
        self.maxconn = 0
        self.minconn = 0
        self.observe = ""
        self.on_error = ""
        self.port = ""
        self.redir = ""
        self.rise = 2
        self.slowstart = 0
        self.source_addres = ""
        self.source_min_port = ""
        self.source_max_port = ""
        self.track = ""
        self.weight = 1



class HaproxyConfigFile:
    def __init__(self, haproxy_config_file_path = '/tmp/haproxy.cfg'):
        self.haproxy_config_file_path = haproxy_config_file_path
        
    def GetHAproxyConfigFileName(self):
        return self.haproxy_config_file_path
 #============ New code =========================   
    def AddFronted(self,  HaproxyFronted):
        """
            Add frontend section to haproxy config file
        """
        new_config_file = self._ReadConfigFile()
        if HaproxyFronted.name =="":
            logger.error("Empty fronted name")
            return "FRONTEND NAME ERROR"
        if HaproxyFronted.bind_address =="" or HaproxyFronted.bind_port == "":
            logger.error("Empty  bind adrress or port")
            return "FRONTEND ADDRESS OR PORT ERROR"
        logger.debug("Adding frontend %s"  % HaproxyFronted.name  )
        new_config_block = []
        new_config_block.append("\tbind %s:%s" % (HaproxyFronted.bind_address,  HaproxyFronted.bind_port))
        new_config_block.append("\tmode %s" % HaproxyFronted.mode)
        new_config_file [ "frontend %s" % HaproxyFronted.name ] =  new_config_block 
        self._WriteConfigFile(new_config_file)
        return  HaproxyFronted.name  

    def DeleteBlock (self, HaproxyBlock):
        """
            Delete fronend section from haproxy config file
        """
        new_config_file = self._ReadConfigFile()
        if HaproxyBlock.name =="":
            logger.error("Empty block name")
            return "BLOCK NAME ERROR"
        logger.debug("Deleting block %s %s"  % (HaproxyBlock.type,  HaproxyBlock.name))
        for i in new_config_file.keys():
            if i.find(HaproxyBlock.type) == 0 and i.find('%s' % HaproxyBlock.name) >= 0:
                del new_config_file[i]
        self._WriteConfigFile(new_config_file)

    def AddBackend(self,  HaproxyBackend):
        """
            Add backend section to haproxy config file
        """
        new_config_file = self._ReadConfigFile()
        if HaproxyBackend.name =="":
            logger.error("Empty backend name")
            return "BACKEND NAME ERROR"
        logger.debug("Adding backend")
        new_config_block = []
        new_config_block.append("\tbalance %s" % HaproxyBackend.balance )
        new_config_file [ "backend %s" % HaproxyBackend.name ] =  new_config_block
        self._WriteConfigFile(new_config_file)
        return  HaproxyBackend.name    
       
       
    def _ReadConfigFile(self):
        self.haproxy_config_file = open (self.haproxy_config_file_path,  "r")
        config_file = {}
        block_name = ''
        current_block = []
        logger.debug ('global')
        for line in  self.haproxy_config_file :
            if  not line.strip(): continue
            tmp_line = line.strip()
            if tmp_line.find('global' )  == 0:  
                config_file [block_name] = current_block
                block_name=line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('defaults' )  == 0:
                config_file [block_name] = current_block
                block_name=line.rstrip()
                current_block = []
                continue              
            elif tmp_line.find('listen' )  == 0:
                config_file [block_name] = current_block
                block_name=line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('backend')  == 0:
                config_file [block_name] = current_block
                block_name=line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('frontend')  == 0:
                config_file [block_name] = current_block
                block_name=line.rstrip()
                current_block = []
                continue
            else:
                current_block.append(line.rstrip())
        #Writing last block
        config_file [block_name] = current_block       
        self.haproxy_config_file.close()
        return config_file
   
    def _WriteConfigFile(self, config_file):
        self.haproxy_config_file  = open (self.haproxy_config_file_path,  "w")
        self.haproxy_config_file.write ("global\n")
        for v  in config_file ['global'] :
            self.haproxy_config_file.write ("%s\n" % v)
        del  config_file ['global'] 
        self.haproxy_config_file.write ("defaults\n")
        for v in config_file['defaults'] :
            self.haproxy_config_file.write ("%s\n" % v)
        del  config_file ['defaults'] 
        for k, v in sorted(config_file.iteritems()):
            self.haproxy_config_file.write ("%s\n" % k)
            for out_line in v:
                self.haproxy_config_file.write ("%s\n" % out_line)
        self.haproxy_config_file.close()
if __name__ == '__main__':
    pass

