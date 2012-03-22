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
        self._sf_id = None
        self._name = ""
        self._type = "Host"
        self._webHostRedir = ""
        self._ipType = "IPv4"
        self._IP = ""
        self._port = ""
        self._state= "InService" #StandBy, OutOfService
        self._opstate = "InService"
        self._description = ""
        self._failOnAll = None
        self._minCon = 4000000
        self._maxCon = 4000000
        self._weight = 8
        self._probes = []
        self._rateBandwidth = ""
        self._rateConn = ""
        self._backupRS = ""
        self._created = None
        self._updated = None

    def loadFromRow(self, row):
        msg = 'LoadBalancer create from row. Id: %s' % row[0]
        logger.debug(msg)
        self._id = row[0]
        self._sf_id = row[1]
        self._name = row[2]
        self._type = row[3]
        self._webHostRedir = row[4]
        self._ipType = row[5]
        self._IP = row[6]
        self._port = row[7]
        self._state= row[8]
        self._opstate = row[9]
        self._description = row[10]
        self._failOnAll = row[11]
        self._minCon = row[12]
        self._maxCon = row[13]
        self._weight = row[14]
        self._probes = row[15]
        self._rateBandwidth = row[16]
        self._rateConn = row[17]
        self._backupRS = row[18]
        self._created = row[19]
        self._updated = row[20]        

    @property
    def id(self):
        return self._id
        
    @id.setter
    def id(self,  value):
        self._id = value

    @property
    def sf_id(self):
        return self._sf_id
        
    @sf_id.setter
    def sf_id(self,  value):
        self._sf_id = value
        
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
    def port(self):
        return self._port
    
    @port.setter
    def port(self, value):
        self._port = value

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
    def backupRS(self):
        return self._backupRS
    @backupRS.setter
    def backupRS(self, value):
        self._backupRS = value
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
