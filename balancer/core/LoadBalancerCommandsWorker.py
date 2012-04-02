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
from balancer.loadbalancers.vserver import makeCreateLBCommandChain, makeDeleteLBCommandChain
from balancer.loadbalancers.vserver import Deployer,  Destructor

logger = logging.getLogger(__name__)

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
       


class LBGetDataWorker(SyncronousWorker):
    def __init__(self,  task):
         super(LBGetDataWorker, self).__init__(task)
         self._t=1
    
    def run(self):
      self._task.status = STATUS_PROGRESS
      store = Storage()
      reader = store.getReader()
      
      id = self._task.parameters['id']
      logger.debug("Getting information about loadbalancer with id: %s" % id)
      list = reader.getLoadBalancerById(id)
      logger.debug("Got information: %s" % list)
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
            lb = bal_deploy.getLB()
            lb.device_id = device.id
            #Step 2. Save config in DB
            bal_deploy.savetoDB()
            
            #Step 3. Deploy config to device
            commands = makeCreateLBCommandChain(bal_deploy,  driver,  context)
            deploy = Deployer()
            deploy.commands = commands
            deploy.execute()
            
            self._task.status = STATUS_DONE
            return lb.id
            
class DeleteLBWorker(SyncronousWorker):            
        def __init__(self,  task):
            super(DeleteLBWorker, self).__init__(task)
            self._command_queue = Queue.LifoQueue()
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            lb_id = self._task.parameters
            sched = Scheduller()
            device = sched.getDeviceByLBid(lb_id)
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            bal_deploy = Balancer()
            bal_deploy.loadFromDB(lb_id)
            
            
            #Step 1. Parse parameters came from request
            #bal_deploy.parseParams(params)
            
            #Step 2. Delete config in DB
            bal_deploy.removeFromDB()
            
            #Step 3. Destruct config at device
            commands = makeDeleteLBCommandChain(bal_deploy,  driver,  context)
            destruct = Destructor()
            destruct.commands = commands
            destruct.execute()
            
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
        if action =="loadbalancer_data":
            return LBGetDataWorker(task)
