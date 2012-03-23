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



from BaseDriver import BaseDriver
from context import Context
from haproxy_config_file_editor import HaproxyConfigFile

from balancer.loadbalancers.loadbalancer import *
from openstack.common import exception
from balancer.devices.device import LBDevice
from balancer.core.configuration import Configuration
from balancer.loadbalancers.probe import *
from balancer.loadbalancers.realserver import RealServer 
logger = logging.getLogger(__name__)

class HaproxyDriver(BaseDriver):
    def __init__(self):
        
        pass

    def createRServer(self, context, rserver):
        if not bool(rserver.name): 
            return 'RSERVER NAME ERROR'
        config_file  = HaproxyConfigFile('/tmp/haproxy.cfg')
        
        pass
    
    
    def deleteRServer(self, context, rserver):
        pass
    
    def activateRServer(self,  context,  serverfarm,  rserver):
        pass
    
    
    def suspendRServer(self,  context,  serverfarm,  rserver):
        pass
    
    
    def createProbe(self,  context,  probe):
        pass
    
    
    def deleteProbe(self,  context,  probe):
        pass
    
    
    def createServerFarm(self,  context,  serverfarm):
        pass
    
    
    def deleteServerFarm(self,  context,  serverfarm):
        pass
    
    def addRServerToSF(self,  context,  serverfarm,  rserver): #rserver in sfarm may include many parameters !
        pass
    
    
    def deleteRServerFromSF(self,  context,  serverfarm,  rserver):
        pass
    
    
    def addProbeToSF(self,  context,  serverfarm,  probe):
        pass
    
    
    def deleteProbeFromSF (elf,  context,  serverfarm,  probe):
        pass
    
    
    def createStickiness(self,  context,  vip,  sticky):
        pass
    
    
    def deleteStickiness(self,  context,  vip,  sticky):
        pass
    
    
    def createVIP(self,  context, vip,  sfarm): 
        pass
    
    
    def deleteVIP(self,  context,  vip):
        pass
    
    
    
    
