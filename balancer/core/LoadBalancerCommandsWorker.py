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
       

class CreateLBWorker(ASyncronousWorker):
        def __init__(self,  task):
            super(CreateLBWorker, self).__init__(task)
            self._command_queue = Queue.LifoQueue()
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            params = self._task.parameters
            driver = params['driver']
            device = params['device']
            context = driver.getContext(device)

            try:
                nodes = params['nodes']
                sf = params['serverfarm']
                
                
                createSF = CreateSFCommand(driver)
                createSF.execute(context, sf)
                self._command_queue.put(createSF)
                
                for node in nodes:
                    createRS = CreateRServerCommand(driver)
                    createRS.execute(context, sf, node)
                    self._command_queue.put(createRS)
                
                probes = params['probes']
                
                for probe in probes:
                    createProbe = CreateProbeCommand(driver)
                    createProbe.execute(context, probe)
                    self._command_queue.put(createProbe)
                    
                    attachProbe = AttachProbeCommand(driver)
                    attachProbe.execute(context, sf,  probe)
                    self._command_queue.put(attachProbe)
                
                vserver = params['vserver']
                
                createVS = CreateVServerCommand(driver)
                createVS.execute(context, sf, vip)
                self._command_queue.put(createVS)
            except exception:
                while not self._command_queue.empty():
                    command = self._command_queue.get()
                    command.undo(context, params)
                self._task.status = STATUS_ERROR
                #TODO Do rollback. We need command pattern here
            
            self._task.status = STATUS_DONE
            
            

class LBActionMapper(object):
    def getWorker(self, task,  action,  params=None):
        if action == "index":
            return LBGetIndexWorker(task)
        if action == "create":
            return CreateLBWorker(task)
              
