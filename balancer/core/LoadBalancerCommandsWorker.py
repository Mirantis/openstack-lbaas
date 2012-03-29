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
from balancer.core.LBCommands import *
from balancer.storage.storage import *
from balancer.core.scheduller import Scheduller
from balancer.devices.DeviceMap import DeviceMap
from balancer.loadbalancers.vserver import Balancer
from balancer.loadbalancers.vserver import makeCreateLBCommandChain
from balancer.loadbalancers.vserver import Deployer


class LBGetIndexWorker(SyncronousWorker):
    def __init__(self,  task):
         super(LBGetIndexWorker, self).__init__(task)
         self._t=1
    
    def run(self):
      self._task.status = STATUS_PROGRESS
      store = Storage()
      reader = store.getReader()
      list = reader.getLoadBalancers()
      self._task.status = STATUS_DONE
      return list
       

class CreateLBWorker(SyncronousWorker):
        def __init__(self,  task):
            super(CreateLBWorker, self).__init__(task)
            self._command_queue = Queue.LifoQueue()
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            params = self._task.parameters
            sched = Scheduller()
            device = sched.getDevice()
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            bal_deploy = Balancer()
            
            #Step 1. Parse parameters came from request
            bal_deploy.parseParams(params)
            
            #Step 2. Save config in DB
            bal_deploy.savetoDB()
            
            #Step 3. Deploy config to device
            commands = makeCreateLBCommandChain(bal_deploy,  driver,  contex)
            deploy = Deployer()
            deploy.commands = commands
            deploy.execute()
            
            self._task.status = STATUS_DONE
            return "OK"
            
class DeleteLBWorker(SyncronousWorker):            
        def __init__(self,  task):
            super(DeleteLBWorker, self).__init__(task)
            self._command_queue = Queue.LifoQueue()
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            #params = self._task.parameters
            sched = Scheduller()
            device = sched.getDevice()
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            bal_deploy = Balancer()
            
            #Step 1. Parse parameters came from request
            bal_deploy.parseParams(params)
            
            #Step 2. Save config in DB
            bal_deploy.savetoDB()
            
            #Step 3. Deploy config to device
            commands = makeCreateLBCommandChain(bal_deploy,  driver,  contex)
            deploy = Deployer()
            deploy.commands = commands
            deploy.execute()
            
            self._task.status = STATUS_DONE
            return "OK"

class LBActionMapper(object):
    def getWorker(self, task,  action,  params=None):
        if action == "index":
            return LBGetIndexWorker(task)
        if action == "create":
            return CreateLBWorker(task)
        if action == "delete":
            return DeleteLBWorker(task)
