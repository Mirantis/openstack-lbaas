# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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
import sys
import threading

from openstack.common import exception
from balancer.devices.device import LBDevice
from balancer.storage.storage import *

class Scheduller(object):
    
    def __init__(self):
        self._device_map = {}
        self._list = None
        store = Storage()
        reader = store.getReader()
        list = reader.getDevices()
        self._list = list
        for device in list:
            self._device_map[device.id] = device
        
        
    def getDevice(self):
        #TODO understand how we select device
        return self._list[0]
        
    def getDeviceByLBid(self, id):
        rd = store.getReader()
        self._device_map = rd.getDeviceByLBid(id)
        return self._device_map
        
    def getDeviceByID(self,  id):
        dev = self._device_map.get(id,  None)
        if dev == None:
            raise  exception.NotFound()
        return dev
    
    def getDevices(self):
        return self._list
        
    def addDevice(self,  device):
         self._device_map[device.id] = device
         self._list.append(device)
  
        
        
