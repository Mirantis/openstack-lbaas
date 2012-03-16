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

SF
 id
 name
 status
 RServer[]
 
RServer
 id
 name
 IP
 port
 status
 
Probe
VS


class LoadBalancer(object):
    def __init__(self):
        self._id = None
        self._name = ""
        self._algorithm = "LEAST_CONNECTIONS"
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
    def algorithm(self):
        return self._algorithm
    
    @algorithm.setter
    def algorithm(self,  value):
        self._algorithm = value
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self,  value):
        self._status = value
    
    @property
    def  created():
        return self._created
    
    @created.setter
    def created(self,  value):
        self._created = value
    
    @property
    def updated(self):
        return self._updated
    
    @updated.setter
    def updated(self,  value):
        self._updated = value
