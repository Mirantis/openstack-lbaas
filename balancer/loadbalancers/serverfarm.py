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
import predictor

class ServerFarm(Object):
    def __init__(self):
        self._id = None
        self._name = ""
        self._type = "Host"
        self._description = ""
        self._failAction = None
        self._inbandHealthCheck = None
        self._connFailureThreshCount = ""
        self._resetTimeout = ""
        self._resumeService = ""
        self._transparent = None
        self._dynamicWorkloadScale = None
        self._vmProbeName = ""
        self._failOnAll = None
        self._partialThreshPercentage = 0
        self._backInservice = 0
        self._probes = []
        self._rservers = []
        self._predictor = predictor.RoundRobin()
        self._retcodeMap = ""
        self._status = "ACTIVE"
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
    def description(self):
        return self._description
        
    @description.setter
    def description(self, value):
        self._description = value
        
    @property
    def failAction(self):
        return self._failAction
    
    @failAction.setter
    def failAction(self, value):
        self._failAction = value
        
    @property
    def inbandHealthCheck(self):
        return self._inbandHealthCheck
    
    @inbandHealthCheck.setter
    def inbandHealthCheck(self, value):
        self._inbandHealthCheck = value
        
    @property
    def connFailureThreshCount(self):
        return self._connFailureThreshCount
        
    @connFailureThreshCount.setter
    def connFailureThreshCount(self, value):
        self._connFailureThreshCount = value
    _created
    @property
    def resetTimeout(self):
        return self._resetTimeout
        
    @resetTimeout.setter
    def resetTimeout(self, value):
        self._resetTimeout = value
        
    @property
    def resumeService(self):
        return self._resumeService
        
    @resumeService.setter
    def resumeService(self, value):
        self._resumeService = value
        
    @property
    def transparent(self):
        return self._transparent
        
    @transparent.setter
    def transparent(self, value):
        self._transparent = value
        
    @property
    def dynamicWorkloadScale(self):
        return self._dynamicWorkloadScale
    
    @dynamicWorkloadScale.setter
    def dynamicWorkloadScale(self, value):
        self._dynamicWorkloadScale = value
    
    @property
    def vmProbeName(self):
        return self._vmProbeName
    
    @vmProbeName.setter
    def vmProbeName(self, value):
        self._vmProbeName = value
    
    @property
    def failOnAll(self):
        return self._failOnAll
    
    @failOnAll.setter
    def failOnAll(self, value):
        self._failOnAll = value
        
    @property
    def partialThreshPercentage(self):
        return self._partialThreshPercentage
    
    @partialThreshPercentage.setter
    def partialThreshPercentage(self, value):
        self._partialThreshPercentage = value
    
    @property
    def backInservice(self):
        return self._backInservice
    
    @backInservice.setter
    def backInservice(self, value):
        self._backInservice
    
    @property
    def probes(self):
        return self._probes
    
    @probes.setter
    def probes(self, value):
        self._probes = value
        
    @property
    def rservers(self):
        return self._rservers
    
    @rservers.setter
    def rservers(self, value):
        self._rservers = value
    
    @property
    def predictor(self):
        return self._predictor
    
    @predictor.setter
    def predictor(self, value):
        self._predictor = value
        
    @property
    def retcodeMap(self):
        return self._retcodeMap
    
    @retcodeMap.setter
    def retcodeMap(self, value):
        self._retcodeMap = value
        
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value
    
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
