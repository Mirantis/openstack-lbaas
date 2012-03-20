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

class RealServer(object):
    def __init__(self):
        self._id = None
        self._name = ""
        self._type = "Host"
        self._webHostRedir = ""
        self._ipType = "IPv4"
        self._IP = ""
        self._state= "In Service"
        self._opstate = "InService"
        self._description = ""
        self._failOnAll = None
        self._minCon = 4000000
        self._maxCon = 4000000
        self._weight = 8
        self._probes = []
        self._rateBandwidth = ""
        self._rateConn = ""
        self._created = None
        self._updated = None
    
    @property
    def id(self):
        return self._id
        
    @id.setter
    def id(self,  value):
        self._id = value

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def webHostRedir(self):
        return self._webHostRedir

    @webHostRedir.setter
    def webHostRedir(self, value):
        self._webHostRedir = value
        
    @property
    def ipType(self):
        return self._type
    
    @ipType.setter
    def ipType(self, value):
        self._ipType = value

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self,  value):
        self._state = value

    @property
    def opstate(self):
        return self._opstate
    
    @opstate.setter
    def opstate(self,  value):
        self._opstate = value

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self,  value):
        self._description = value

    @property
    def failOnAll(self):
        return self._failOnAll
    
    @failOnAll.setter
    def failOnAll(self,  value):
        self._failOnAll = value

    @property
    def minCon(self):
        return self._minCon
    
    @minCon.setter
    def minCon(self,  value):
        self._minCon = value

    @property
    def maxCon(self):
        return self._maxCon
    
    @maxCon.setter
    def maxCon(self,  value):
        self._maxCon = value

    @property
    def weight(self):
        return self._weight
    
    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def probes(self):
        return self._probes
    
    @probes.setter
    def probes(self, value):
        self._probes = value

    @property
    def rateBandwidth(self):
        return self._rateBandwidth
    
    @rateBandwidth.setter
    def rateBandwidth(self, value):
        self._rateBandwidth = value

    @property
    def rateConn(self):
        return self._rateConn
        
    @rateConn.setter
    def rateConn(self, value):
        self._rateConn = value
        
    @property
    def  created():
        return self._created
    
    @created.setter
    def created(self,  value):
        self._created = value

    @property
    def  updated():
        return self._created
    
    @created.setter
    def updated(self,  value):
        self._updated = value
