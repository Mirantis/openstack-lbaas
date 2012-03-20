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
#    under the License.

import logging
import vlan

class VirtualServer(object):
    def __init__(self):
        self._id = None
        self._sf_id = None
        self._name = ""
        self._ipType = "IPv4"
        self._ip = ""
        self._virtIPmask = "255.255.255.255"
        self._proto = "TCP"
        self._appProto = "Other"
        self._Port = "any"
        self._allVLANs = None
        self._VLAN = [] #need to describe in new module
        self._connParameterMap = None #need to describe in new module
        self._KALAPtagName = ""
        self._KALAPprimaryOutOfServ = None
        self._ICMPreply = "None"
        self._status = "In Service"
        
        self._protocolInspect = None #need to describe in new module
        self._appAccelAndOpt = None #need to describe in new module
        self._L7LoadBalancing = None #need to describe in new module
        self._serverFarm = None
        self._backupServerFarm = None
        self._SSLproxyServName = None #need to describe in new module
        self._defaultL7LBAction = None #need to describe in new module
        self._SSLinitiation = None #need to describe in new module
        self._NAT = [] #need to describe in new module
        self._created = None
        self._updated = None
    
    @property
    def id(self):
        return self._id 
    @id.setter
    def id(self, value):
        self._id  = value
    @property
    def sf_id(self):
        return self._sf_id 
    @sf_id.setter
    def sf_id(self, value):
        self._sf_id  = value
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    @property
    def ipType(self):
        return self._ipType
    @ipType.setter
    def ipType(self, value):
        self._ipType = value
    @property
    def ip(self):
        return self._ip
    @ip.setter
    def ip(self, value):
        self._ip = value
    @property
    def virtIPmask(self):
        return self._virtIPmask
    @virtIPmask.setter
    def virtIPmask(self, value):
        self._virtIPmask = value
    @property
    def proto(self):
        return self._proto
    @proto.setter
    def proto(self, value):
        self, _proto = value
    @property
    def appProto(self):
        return self._appProto
    @appProto.setter
    def appProto(self, value):
        self._appProto = value
    @property
    def Port(self):
        return self._Port
    @Port.setter
    def Port(self, value):
        self._Port = value
    @property
    def allVLANs(self):
        return self._allVLANs
    @allVLANs.setter
    def allVLANs(self, value):
        self._allVLANs = value
    @property
    def VLAN(self):
        return self._VLAN
    @VLAN.setter
    def VLAN(self, value):
        self._VLAN = value
    @property
    def connParameterMap(self):
        return self._connParameterMap
    @connParameterMap.setter
    def connParameterMap(self, value):
        self._connParameterMap = value
    @property
    def KALAPtagName(self):
        return self._KALAPtagName
    @KALAPtagName.setter
    def KALAPtagName(self, value):
        self._KALAPtagName = value
    @property
    def KALAPprimaryOutOfServ(self):
        return self._KALAPprimaryOutOfServ
    @KALAPprimaryOutOfServ.setter
    def KALAPprimaryOutOfServ(self, value):
        self._KALAPprimaryOutOfServ = value
    @property
    def ICMPreply(self):
        return self._ICMPreply
    @ICMPreply.setter
    def ICMPreply(self, value):
        self._ICMPreply = value
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        self._status = value
    @property
    def protocolInspect(self):
        return self._protocolInspect
    @protocolInspect.setter
    def protocolInspect(self, value):
        self._protocolInspect = value
    @property
    def appAccelAndOpt(self):
        return self._appAccelAndOpt
    @appAccelAndOpt.setter
    def appAccelAndOpt(self, value):
        self._appAccelAndOpt = value
    @property
    def L7LoadBalancing(self):
        return self._L7LoadBalancing
    @L7LoadBalancing.setter
    def L7LoadBalancing(self, value):
        self._L7LoadBalancing = value
    @property
    def serverFarm(self):
        return self._serverFarm
    @serverFarm.setter
    def serverFarm(self, value):
        self._serverFarm = value
    @property
    def backupServerFarm(self):
        return self._backupServerFarm
    @backupServerFarm.setter
    def backupServerFarm(self, value):
        self._backupServerFarm = value
    @property
    def SSLproxyServName(self):
        return self._SSLproxyServName
    @SSLproxyServName.setter
    def SSLproxyServName(self, value):
        self._SSLproxyServName = value
    @property
    def defaultL7LBAction(self, value):
        return self._defaultL7LBAction
    @defaultL7LBAction.setter
    def defaultL7LBAction(self, value):
        self._defaultL7LBAction = value
    @property
    def SSLinitiation(self):
        return self._SSLinitiation
    @SSLinitiation.setter
    def SSLinitiation(self, value):
        self._SSLinitiation = value
    @property
    def NAT(self):
        return self._NAT
    @NAT.setter
    def NAT(self, value):
        self._NAT = value
    @property
    def created(self):
        return self._created
    @created.setter
    def created(self, value):
        self._created = value
    @property
    def updated(self):
        return self._updated
    @updated.setter
    def updated(self, value):
        self._updated = value
