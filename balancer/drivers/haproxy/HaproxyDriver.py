# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License


import sys
import os
import logging


from balancer.drivers.BaseDriver import BaseDriver
from balancer.drivers.haproxy.Context import Context
from balancer.drivers.haproxy.RemoteControl import RemoteConfig
from balancer.drivers.haproxy.RemoteControl import RemoteService
from balancer.drivers.haproxy.RemoteControl import RemoteInterface

logger = logging.getLogger(__name__)

class HaproxyDriver(BaseDriver):
    def __init__(self):
        pass

    def getContext (self,  dev):
        return Context(dev.ip , dev.port , dev.user , dev.password, dev.localpath, dev.configfilepath, \
                       dev.remotepath, dev.interface )

    def addRServerToSF(self,  context,  serverfarm,  rserver):
        haproxy_serverfarm = HaproxyBackend ()
        haproxy_serverfarm.name = serverfarm.name
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver.name
        haproxy_rserver.weight = rserver.weight
        haproxy_rserver.address = rserver.address
        haproxy_rserver.port = rserver.port
        haproxy_rserver.maxconn = rserver.maxCon
        #Modify remote config file, check and restart remote haproxy
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)
        logger.debug('[HAPROXY] Creating rserver %s in the backend block %s' % \
                              (haproxy_rserver.name,  haproxy_serverfarm.name))
        remote.getConfig()
        config_file.AddRserverToBackendBlock (haproxy_serverfarm, haproxy_rserver )
        remote.putConfig()

    def deleteRServerFromSF(self, context,  serverfarm,  rserver):
        haproxy_serverfarm = HaproxyBackend ()
        haproxy_serverfarm.name = serverfarm.name
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver.name
        #Modify remote config file, check and restart remote haproxy
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)
        logger.debug('[HAPROXY] Deleting rserver %s in the backend block %s' %  \
                            (haproxy_rserver.name,  haproxy_serverfarm.name))
        remote.getConfig()        
        config_file.DelRserverFromBackendBlock(haproxy_serverfarm, haproxy_rserver)
        remote.putConfig()
    
    def createVIP(self,  context, virtualserver,  serverfarm): 
        if not bool(virtualserver.name):
            logger.error ('[HAPROXY] Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver.name
        haproxy_virtualserver.bind_address = virtualserver.address
        haproxy_virtualserver.bind_port = virtualserver.port
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm.name
        #Add new IP address
        remote_interface = RemoteInterface(context, haproxy_virtualserver )
        remote_interface.addIP()
        #Modify remote config file, check and restart remote haproxy
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)

    
    def deleteVIP(self,  context,  virtualserver):
        if not bool(virtualserver.name):
            logger.error ('[HAPROXY] Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver.name
        haproxy_virtualserver.bind_address = virtualserver.address
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)
        #Check ip for using in the another frontend
        if  not config_file.FindStringInTheBlock ('frontend',  haproxy_virtualserver.bind_address ):
            logger.debug('[HAPROXY] ip %s does not using in the othe frontend, delete it from remote interface' % \
                         haproxy_virtualserver.bind_address )
            remote_interface = RemoteInterface(context, haproxy_virtualserver )
            remote_interface.delIP ()
        remote.getConfig() 
        config_file.DeleteBlock(haproxy_virtualserver) 
        remote.putConfig()
        


    def createServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            logger.error ('[HAPROXY] Serverfarm name is empty')
            return 'SERVERFARM FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm.name
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)
        remote.getConfig() 
        config_file.AddBackend(haproxy_serverfarm)
        remote.putConfig()

    def deleteServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            logger.error ('[HAPROXY] Serverfarm name is empty')
            return 'SERVER FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm.name
        config_file = HaproxyConfigFile('%s/%s' % (context.localpath,  context.configfilename))
        remote = RemoteConfig(context)
        remote.getConfig()
        config_file.DeleteBlock(haproxy_serverfarm)       
        remote.putConfig()

class HaproxyConfigBlock:
    def __init__(self):
        self.name = ''
        self.type = ''
        
class HaproxyFronted(HaproxyConfigBlock):
    def __init__(self):
        self.type='frontend'
        self.bind_address = ''
        self.bind_port= ''
        self.default_backend = ''
        self.mode = 'http'

class HaproxyBackend(HaproxyConfigBlock):
    def __init__(self):
        self.type='backend'
        self.mode = ''
        self.balance = 'source'
        
class HaproxyListen(HaproxyConfigBlock):
    def __init__(self):
        self.type='listen'
        self.name = ''
        self.mode = ''
        self.balance = 'source'
   
class HaproxyRserver():
    def __init__(self):
        self.name = ''
        self.address = ''
        self.check = 'check'
        self.cookie = ''
        self.disabled = False
        self.error_limit = 10
        self.fall = '3'
        self.id = ''
        self.inter = 2000
        self.fastinter = 2000
        self.downinter = 2000
        self.maxconn = 32
        self.minconn = 0
        self.observe = ''
        self.on_error = ''
        self.port = ''
        self.redir = ''
        self.rise = '2'
        self.slowstart = 0
        self.source_addres = ''
        self.source_min_port = ''
        self.source_max_port = ''
        self.track = ''
        self.weight = 1



class HaproxyConfigFile:
    def __init__(self, haproxy_config_file_path = '/tmp/haproxy.cfg'):
        self.haproxy_config_file_path = haproxy_config_file_path
        
    def GetHAproxyConfigFileName(self):
        return self.haproxy_config_file_path

    def AddRserverToBackendBlock(self,  HaproxyBackend,  HaproxyRserver):
        '''
            Add real server to backend section config file
        '''
        new_config_file = self._ReadConfigFile()
        logger.debug('[HAPROXY] backend %s rserver %s' % (HaproxyBackend.name,  HaproxyRserver.name))
        if HaproxyBackend.name =='':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        for i in new_config_file.keys():
            if i.find(HaproxyBackend.type) == 0 and i.find('%s' % HaproxyBackend.name) >= 0:
                new_config_file[i].append('\tserver %s %s:%s %s maxconn %s inter %s rise %s fall %s' %  \
                                           (HaproxyRserver.name,  HaproxyRserver.address, HaproxyRserver.port,   \
                                            HaproxyRserver.check,  HaproxyRserver.maxconn,  HaproxyRserver.inter, \
                                             HaproxyRserver.rise, HaproxyRserver.fall ) )
        self._WriteConfigFile(new_config_file)
 
    def DelRserverFromBackendBlock(self,  HaproxyBackend,  HaproxyRserver):
        '''
            Delete real server to backend section config file
        '''
        new_config_file = self._ReadConfigFile()
        logger.debug('[HAPROXY] From backend %s delete rserver %s' % (HaproxyBackend.name,  HaproxyRserver.name))
        if HaproxyBackend.name =='':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        for i in new_config_file.keys():
            if i.find(HaproxyBackend.type) == 0 and i.find('%s' % HaproxyBackend.name) >= 0:
                for j in new_config_file[i]:
                    logger.debug ('[HAPROXY] found %s' % new_config_file[i])
                    if j.find('server') >= 0 and j.find(HaproxyRserver.name) >= 0: new_config_file[i].remove(j)
        self._WriteConfigFile(new_config_file)

    def AddFronted(self,  HaproxyFronted,  HaproxyBackend = None):
        '''
            Add frontend section to haproxy config file
        '''
        new_config_file = self._ReadConfigFile()
        if HaproxyFronted.name =='':
            logger.error('[HAPROXY] Empty fronted name')
            return 'FRONTEND NAME ERROR'
        if HaproxyFronted.bind_address =='' or HaproxyFronted.bind_port == '':
            logger.error('[HAPROXY] Empty  bind adrress or port')
            return 'FRONTEND ADDRESS OR PORT ERROR'
        logger.debug('[HAPROXY] Adding frontend %s'  % HaproxyFronted.name  )
        new_config_block = []
        new_config_block.append('\tbind %s:%s' % (HaproxyFronted.bind_address,  HaproxyFronted.bind_port))
        new_config_block.append('\tmode %s' % HaproxyFronted.mode)
        if HaproxyBackend is not None :
            new_config_block.append('\tdefault_backend %s' % HaproxyBackend.name )
        new_config_file [ 'frontend %s' % HaproxyFronted.name ] =  new_config_block 
        self._WriteConfigFile(new_config_file)
        return  HaproxyFronted.name  

    def DeleteBlock (self, HaproxyBlock):
        '''
            Delete fronend section from haproxy config file
        '''
        new_config_file = self._ReadConfigFile()
        if HaproxyBlock.name =='':
            logger.error('[HAPROXY] Empty block name')
            return 'BLOCK NAME ERROR'
        logger.debug('[HAPROXY] Try to delete block %s %s'  % (HaproxyBlock.type,  HaproxyBlock.name))
        for i in new_config_file.keys():
            if i.find(HaproxyBlock.type) == 0 and i.find('%s' % HaproxyBlock.name) >= 0:
                logger.debug('[HAPROXY] Delete block %s %s'  % (HaproxyBlock.type,  HaproxyBlock.name))
                del new_config_file[i]
        self._WriteConfigFile(new_config_file)
    
    def FindStringInTheBlock(self,  block_type,  check_string):
        """
            Find string in the blocks
        """
        new_config_file = self._ReadConfigFile()
        for i in new_config_file.keys():
            if i.find(block_type) == 0 and new_config_file[i].find(check_string) >= 0 :
                return True
            else:
                return False
    
    def AddBackend(self,  HaproxyBackend):
        '''
            Add backend section to haproxy config file
        '''
        new_config_file = self._ReadConfigFile()
        if HaproxyBackend.name =='':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        logger.debug('[HAPROXY] Adding backend')
        new_config_block = []
        new_config_block.append('\tbalance %s' % HaproxyBackend.balance )
        new_config_file [ 'backend %s' % HaproxyBackend.name ] =  new_config_block
        self._WriteConfigFile(new_config_file)
        return  HaproxyBackend.name    
       
    def _ReadConfigFile(self):
        haproxy_config_file = open (self.haproxy_config_file_path,  'r')
        config_file = {}
        block_name = ''
        current_block = []
        for line in  haproxy_config_file :
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
        haproxy_config_file.close()
        return config_file
   
    def _WriteConfigFile(self, config_file):
        haproxy_config_file  = open (self.haproxy_config_file_path,  'w+')
        logging.debug('[HAPROXY] writing configuration to %s' % self.haproxy_config_file_path)
        haproxy_config_file.write ('global\n')
        for v  in config_file ['global'] :
            haproxy_config_file.write ('%s\n' % v)
        del  config_file ['global'] 
        haproxy_config_file.write ('defaults\n')
        for v in config_file['defaults'] :
            haproxy_config_file.write ('%s\n' % v)
        del  config_file ['defaults'] 
        for k, v in sorted(config_file.iteritems()):
            haproxy_config_file.write ('%s\n' % k)
            for out_line in v:
                haproxy_config_file.write ('%s\n' % out_line)
        haproxy_config_file.close()
        
if __name__ == '__main__':
    pass

