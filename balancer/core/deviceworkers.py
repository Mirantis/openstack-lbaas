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
import Queue

from balancer.core.Worker import *
from balancer.storage.storage import *
from balancer.core.ServiceController import *

class DeviceGetIndexWorker(SyncronousWorker):
    def __init__(self,  task):
         super(DeviceGetIndexWorker,  self).__init__(task)
    
    def run(self):
      self._task.status = STATUS_PROGRESS
      store = Storage()
      reader = store.getReader()
      list = reader.getDevices()
      self._task.status = STATUS_DONE
      return list
       

class DeviceCreateWorker(SyncronousWorker):
    def __init__(self,  task):
          super(DeviceCreateWorker, self).__init__(task)
    
    def run(self):
      self._task.status = STATUS_PROGRESS
      params = self._task.parameters
      dev = LBDevice()
      dev.name = params['name']
      dev.type = params['type']
      dev.version =  params['version']
      dev.supports_IPv6 =  params['supports_IPv6']
      dev.require_VIP_IP =  params['requires_VIP_IP']
      dev.has_ACL =  params['has_ACL']
      dev.supports_VLAN =  params['supports_VLAN']
      dev.ip =  params['ip']
      dev.port =  params['port']
      dev.user =  params['user']
      dev.password =  params['password']
      store = Storage()
      writer = store.getWriter()
      writer.writeDevice(dev)
      sc = ServiceController.Instance()
      sched = sc.scheduller
      sched.addDevice(dev)
      self._task.status = STATUS_DONE
      return 'OK'
      
      
      
class DeviceActionMapper(object):
    def getWorker(self, task,  action,  params=None):
        if action == "index":
            return DeviceGetIndexWorker(task)
        if action == "create":
            return DeviceCreateWorker(task)
              
       
