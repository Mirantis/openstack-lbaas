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
import balancer.loadbalancers.loadbalancer
import openstack.common.exception

from balancer.core.Worker import *
from balancer.core.LBCommands import *
from balancer.storage.storage import *
from balancer.core.scheduller import Scheduller
from balancer.devices.DeviceMap import DeviceMap
from balancer.loadbalancers.vserver import Balancer
from balancer.loadbalancers.vserver import makeCreateLBCommandChain, makeDeleteLBCommandChain, makeUpdateLBCommandChain, makeAddNodeToLBChain, makeDeleteNodeFromLBChain, makeChangeNodeStatus
from balancer.loadbalancers.vserver import Deployer,  Destructor, createPredictor

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
      
class LBshowDetails(SyncronousWorker):
    def __init__(self,  task):
         super(LBshowDetails, self).__init__(task)
    
    def run(self):
      self._task.status = STATUS_PROGRESS
      store = Storage()
      reader = store.getReader()
      
      id = self._task.parameters['id']
      lb = Balancer()
      lb.loadFromDB(id)
      obj = {'loadbalancer':  lb.lb.convertToDict()}
      lbobj = obj ['loadbalancer']      
      lbobj['nodes'] = lb.rs
      lbobj['virtualIps'] = lb.vips
      lbobj['healthMonitor'] = lb.probes
      logger.debug("Getting information about loadbalancer with id: %s" % id)
      #list = reader.getLoadBalancerById(id)
      logger.debug("Got information: %s" % lbobj)
      self._task.status = STATUS_DONE
      return lbobj
      
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
            balancer_instance = Balancer()
            
            #Step 1. Parse parameters came from request
            balancer_instance.parseParams(params)
            lb = balancer_instance.getLB()
            lb.device_id = device.id
            #Step 2. Save config in DB
            balancer_instance.savetoDB()
            
            #Step 3. Deploy config to device
            commands = makeCreateLBCommandChain(balancer_instance,  driver,  context)
            deploy = Deployer()
            deploy.commands = commands
            try:
                deploy.execute()
            except openstack.common.exception.Error:
                balancer_instance.lb.status = balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
                balancer_instance.update()
                return
            except openstack.common.exception.Invalid:
                balancer_instance.lb.status = balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
                balancer_instance.update()
                return

            balancer_instance.lb.status = balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
            balancer_instance.update()
            self._task.status = STATUS_DONE
            return lb.id

class UpdateLBWorker(ASyncronousWorker):
        def __init__(self,  task):
            super(UpdateLBWorker, self).__init__(task)
            self._command_queue = Queue.LifoQueue()
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            params = self._task.parameters
            lb_id = params['id']
            sched = Scheduller()
            
            #Step1. Load LB from DB
            
            old_balancer_instance = Balancer()
            balancer_instance = Balancer()
            logger.debug("Loading LB data from DB for Lb id: %s" % lb_id)
            #TODO add clone function to Balancer in order to avoid double read
            balancer_instance.loadFromDB(lb_id)
            old_balancer_instance.loadFromDB(lb_id)
            
            #Step 1. Parse parameters came from request
            body = params['body']
            lb = balancer_instance.lb
            old_predictor_id = None
            port_updated = False
            for key in body.keys():
                if hasattr(lb,key):
                    logger.debug("updating attribute %s of LB. Value is %s"%(key, body[key]))        	
                    setattr(lb,key, body[key])
                    if key.lower()=="algorithm":
                        old_predictor_id = balancer_instance.sf._predictor.id
                        balancer_instance.sf._predictor = createPredictor(body[key])
                else:
                    logger.debug("Got unknown attribute %s of LB. Value is %s"%(key, body[key]))        	
            #Step2: Save updated data in DB
            lb.status = balancer.loadbalancers.loadbalancer.LB_PENDING_UPDATE_STATUS
            balancer_instance.update()
            #Step3. Update device config

            
            
            device = sched.getDeviceByID(lb.device_id)
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            
            
            
            #Step 4. Deploy new config to device
            commands = makeUpdateLBCommandChain(old_balancer_instance, balancer_instance,  driver,  context)
            deploy = Deployer()
            deploy.commands = commands
            try:
                deploy.execute()
            except:
                old_balancer_instance.lb.status = balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
                old_balancer_instance.update()
                return
                
            balancer_instance.lb.status = balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
            balancer_instance.update()
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
            balancer_instance = Balancer()
            balancer_instance.loadFromDB(lb_id)

            device = sched.getDeviceByID(balancer_instance.lb.device_id)
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            
            
            #Step 1. Parse parameters came from request
            #bal_deploy.parseParams(params)
            
            #Step 2. Delete config in DB
            balancer_instance.removeFromDB()
            
            #Step 3. Destruct config at device
            commands = makeDeleteLBCommandChain(balancer_instance,  driver,  context)
            destruct = Destructor()
            destruct.commands = commands
            destruct.execute()
            
            self._task.status = STATUS_DONE
            return "OK"

class LBaddNode(SyncronousWorker):
        def __init__(self,  task):
            super(LBaddNode, self).__init__(task)
            self._command_queue = Queue.LifoQueue()   
        
        def run(self):
            self._task.status = STATUS_PROGRESS
            lb_id = self._task.parameters['id']
            node = self._task.parameters['node']
            logger.debug("Got new node description %s" %node)  
            rs = RealServer()
            sched = Scheduller()
            bal_instance = Balancer()
            
            bal_instance.loadFromDB(lb_id)
            bal_instance.removeFromDB()
            rs.loadFromDict(node)
            rs.sf_id = bal_instance.sf.id
            rs.name = rs.id

            bal_instance.rs.append(rs)
            bal_instance.sf._rservers.append(rs)
            bal_instance.savetoDB()
            
            device = sched.getDeviceByID(bal_instance.lb.device_id)
            devmap = DeviceMap()
            driver = devmap.getDriver(device)
            context = driver.getContext(device)
            
            commands = makeAddNodeToLBChain(bal_instance, driver, context, rs)
            deploy = Deployer()
            deploy.commands = commands
            deploy.execute()
            self._task.status = STATUS_DONE
            return "OK"

class LBShowNodes(SyncronousWorker):
    def __init__(self,  task):
        super(LBShowNodes, self).__init__(task)
        self._command_queue = Queue.LifoQueue()      
            
    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']        

        bal_instance = Balancer()
        nodes = {'nodes':[]}
        
        bal_instance.loadFromDB(lb_id)
        for rs in bal_instance.rs:
            nodes['nodes'].append(rs.convertToDict())
        
        self._task.status = STATUS_DONE
        return nodes
            
class LBDeleteNode(SyncronousWorker):
    def __init__(self,  task):
        super(LBDeleteNode, self).__init__(task)
        self._command_queue = Queue.LifoQueue()  
    
    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']    
        nodeID = self._task.parameters['nodeID']
        
        bal_instance = Balancer()
        bal_instance.loadFromDB(lb_id)
        sched = Scheduller()
        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device)
        
        #Step 1: Load balancer from DB
        bal_instance.loadFromDB(lb_id)
        
        store = Storage()
        
        #Step 2: Get reader and writer
        rd = store.getReader()
        dl = store.getDeleter()
        #Step 3: Get RS object from DB
        rs = rd.getRServerById(nodeID)
        
        #Step 4: Delete RS from DB
        dl.deleteRSbyID(nodeID)
        
        #Step 5: Make commands for deleting RS
        
        commands = makeDeleteNodeFromLBChain(bal_instance, driver, context, rs)
        destruct = Destructor()
        destruct.commands = commands
        
        #Step 6: Delete real server from device
        destruct.execute()
        self._task.status = STATUS_DONE
        return "OK"

class LBChangeNodeStatus(SyncronousWorker):
    def __init__(self,  task):
        super(LBChangeNodeStatus, self).__init__(task)
        self._command_queue = Queue.LifoQueue()  
    
    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']    
        nodeID = self._task.parameters['nodeID']
        nodeStatus = self._task.parameters['status']
        
        bal_instance = Balancer()
        bal_instance.loadFromDB(lb_id)
        sched = Scheduller()
        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device) 
        store = Storage()
        reader = store.getReader()
        writer = store.getWriter()
        deleter = store.getDeleter()
        
        rs = reader.getRServerById(nodeID)
        if rs.state == nodeStatus:
            return "OK"
        logger.debug("Got rs description %s" %rs.convertToDict()) 
        rs.state = nodeStatus
        rsprop = rs.convertToDict()
        deleter.deleteRSbyID(nodeID)
        logger.debug("Write updated rs as %s" %rs.convertToDict()) 
        writer.writeRServer(rs)
        new_rs = RealServer()
        new_rs.loadFromDict(rsprop)

        deploy = Deployer()
        commands = makeChangeNodeStatus(bal_instance, driver, context, rs, new_rs)
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
        if action =="show":
            return LBGetDataWorker(task)
        if action =="showDetails":
            return LBshowDetails(task)
        if action == "update":
            return UpdateLBWorker(task)
        if action == "addNode":
            return LBaddNode(task)
        if action == "showNodes":
            return LBShowNodes(task)
        if action == "deleteNode":
            return LBDeleteNode(task)
        if action == "changeNodeStatus":
            return LBChangeNodeStatus(task)
