# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import logging
import Queue
import balancer.loadbalancers.loadbalancer
import openstack.common.exception

from balancer.core.Worker import *
from balancer.core.LBCommands import *
from balancer.storage.storage import *
from balancer.core.scheduller import Scheduller
from balancer.devices.DeviceMap import DeviceMap
from balancer.loadbalancers.vserver import Balancer
from balancer.loadbalancers.vserver import makeCreateLBCommandChain, \
makeDeleteLBCommandChain, makeUpdateLBCommandChain, makeAddNodeToLBChain, \
makeDeleteNodeFromLBChain, makeAddStickyToLBChain, makeDeleteStickyFromLBChain
from balancer.loadbalancers.vserver import makeAddProbeToLBChain, \
makeDeleteProbeFromLBChain,  ActivateRServerCommand,  SuspendRServerCommand
from balancer.loadbalancers.vserver import Deployer,  Destructor, \
createPredictor,  createProbe,  createSticky

import balancer.processing.event
from balancer.processing.processing import Processing


logger = logging.getLogger(__name__)


class LBGetIndexWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBGetIndexWorker, self).__init__(task, conf)
        self._t = 1

    def run(self):
        self._task.status = STATUS_PROGRESS
        list = core_api.lb_get_index(self._conf, **self._task.parameters)
        self._task.status = STATUS_DONE
        return list

class LBFindforVM(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBFindforVM, self).__init__(task, conf)
        self._t = 1

    def run(self):
        self._task.status = STATUS_PROGRESS
        list = core_api.lb_find_for_vm(self._conf, **self._task.parameters)
        self._task.status = STATUS_DONE
        return list
        
class LBGetDataWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBGetDataWorker, self).__init__(task, conf)
        self._t = 1

    def run(self):
        self._task.status = STATUS_PROGRESS
        list = core_api.lb_get_data(self._conf, self._task.parameters['id'])
        self._task.status = STATUS_DONE
        return list


class LBshowDetails(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBshowDetails, self).__init__(task, conf)

    def run(self):
        self._task.status = STATUS_PROGRESS
        lbobj = core_api.lb_show_details(self._conf, self._task.parameters['id'])
        self._task.status = STATUS_DONE
        return lbobj


class CreateLBWorker(ASyncronousWorker):
    def __init__(self,  task, conf):
        super(CreateLBWorker, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        id = core_api.create_lb(self._conf, **self._task.parameters)
        self._task.status = STATUS_DONE
        return id

class UpdateLBWorker(ASyncronousWorker):
    def __init__(self,  task, conf):
        super(UpdateLBWorker, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        id =  core_api.update_lb(self._conf, self._task.parameters['id'],
                                             self._task.parameters['body'])
        self._task.status = STATUS_DONE
        return id

class DeleteLBWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(DeleteLBWorker, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        core_api.delete_lb(self._conf, self._task.parameters['id'])
        self._task.status = STATUS_DONE
        return "OK"


class LBaddNode(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBaddNode, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        id = core_api.lb_add_node(self._conf, self._task.parameters['id'],
                                              self._task.parameters['node'])
        self._task.status = STATUS_DONE
        return "node: %s" % id


class LBShowNodes(SyncronousWorker, conf):
    def __init__(self,  task):
        super(LBShowNodes, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        nodes = core_api.lb_show_nodes(self._conf, self._task.parameters['id'])
        self._task.status = STATUS_DONE
        return nodes


class LBDeleteNode(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBDeleteNode, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_node_id = core_api.lb_delete_node(self._conf,
                                             self._task.parameters['id'],
                                             self._task.parameters['nodeID'])
        self._task.status = STATUS_DONE
        return "Deleted node with id %s" % lb_node_id


class LBChangeNodeStatus(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBChangeNodeStatus, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        msg = core_api.lb_change_node_status(self._conf,
                                             self._task.parameters['id'],
                                             self._task.parameters['nodeID'],
                                             self._task.parameters['status'])
        self._task.status = STATUS_DONE
        return msg


class LBUpdateNode(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBUpdateNode, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        msg = core_api.lb_update_node(self._conf,
                                      self._task.parameters['id'],
                                      self._task.parameters['nodeID'],
                                      self._task.parameters['node'])
        self._task.status = STATUS_DONE
        return msg


class LBShowProbes(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBShowProbes, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        dict = core_api.lb_show_probes(self._conf, self._task.parameters['id'])
        self._task.status = STATUS_DONE
        return dict


class LBAddProbe(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBAddProbe, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']
        probe = self._task.parameters['probe']
        logger.debug("Got new probe description %s" % probe)
        if probe['type'] == None:
            return

        sched = Scheduller(self._conf)
        bal_instance = Balancer(self._conf)

        bal_instance.loadFromDB(lb_id)
        bal_instance.removeFromDB()
        prb = createProbe(probe['type'])
        prb.loadFromDict(probe)
        prb.sf_id = bal_instance.sf.id
        prb.name = prb.id

        bal_instance.probes.append(prb)
        bal_instance.sf._probes.append(prb)
        bal_instance.savetoDB()

        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device)

        commands = makeAddProbeToLBChain(bal_instance, driver, context, prb, self._conf)
        deploy = Deployer()
        deploy.commands = commands
        deploy.execute()
        self._task.status = STATUS_DONE
        return "probe: %s" % prb.id


class LBdeleteProbe(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBdeleteProbe, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']
        probeID = self._task.parameters['probeID']

        bal_instance = Balancer(self._conf)
        #Step 1: Load balancer from DB
        bal_instance.loadFromDB(lb_id)
        sched = Scheduller(self._conf)
        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device)

        store = Storage(self._conf)

        #Step 2: Get reader and writer
        rd = store.getReader()
        dl = store.getDeleter()
        #Step 3: Get RS object from DB
        prb = rd.getProbeById(probeID)

        #Step 4: Delete RS from DB
        dl.deleteProbeByID(probeID)

        #Step 5: Make commands for deleting probe

        commands = \
            makeDeleteProbeFromLBChain(bal_instance, driver, context, prb, self._conf)
        destruct = Destructor()
        destruct.commands = commands

        #Step 6: Delete real server from device
        destruct.execute()
        self._task.status = STATUS_DONE
        return "Deleted probe with id %s" % probeID


class LBShowSticky(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBShowSticky, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']
        store = Storage(self._conf)
        reader = store.getReader()

        sf_id = reader.getSFByLBid(lb_id).id
        stickies = reader.getStickiesBySFid(sf_id)

        list = []
        dict = {"sessionPersistence": {}}
        for st in stickies:
            list.append(st.convertToDict())
        self._task.status = STATUS_DONE
        dict['sessionPersistence'] = list
        return dict


class LBAddSticky(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBAddSticky, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']
        sticky = self._task.parameters['sticky']
        logger.debug("Got new sticky description %s" % sticky)
        if sticky['type'] == None:
            return

        sched = Scheduller(self._conf)
        bal_instance = Balancer(self._conf)

        bal_instance.loadFromDB(lb_id)
        bal_instance.removeFromDB()
        st = createSticky(sticky['type'])
        st.loadFromDict(sticky)
        st.sf_id = bal_instance.sf.id
        st.name = st.id

        bal_instance.sf._sticky.append(st)
        bal_instance.savetoDB()

        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device)

        commands = makeAddStickyToLBChain(bal_instance, driver, context, st, self._conf)
        deploy = Deployer()
        deploy.commands = commands
        deploy.execute()
        self._task.status = STATUS_DONE
        return "sticky: %s" % st.id


class LBdeleteSticky(SyncronousWorker):
    def __init__(self,  task, conf):
        super(LBdeleteSticky, self).__init__(task, conf)
        self._command_queue = Queue.LifoQueue()

    def run(self):
        self._task.status = STATUS_PROGRESS
        lb_id = self._task.parameters['id']
        stickyID = self._task.parameters['stickyID']

        bal_instance = Balancer(self._conf)
        #Step 1: Load balancer from DB
        bal_instance.loadFromDB(lb_id)
        sched = Scheduller(self._conf)
        device = sched.getDeviceByID(bal_instance.lb.device_id)
        devmap = DeviceMap()
        driver = devmap.getDriver(device)
        context = driver.getContext(device)

        store = Storage(self._conf)

        #Step 2: Get reader and writer
        rd = store.getReader()
        dl = store.getDeleter()
        #Step 3: Get sticky object from DB
        st = rd.getStickyById(stickyID)

        #Step 4: Delete sticky from DB
        dl.deleteStickyByID(stickyID)

        #Step 5: Make commands for deleting probe

        commands = \
            makeDeleteStickyFromLBChain(bal_instance, driver, context, st, self._conf)
        destruct = Destructor()
        destruct.commands = commands

        #Step 6: Delete real server from device
        destruct.execute()
        self._task.status = STATUS_DONE
        return "Deleted sticky with id %s" % stickyID
        
        
class LBActionMapper(object):
    def getWorker(self, task,  action, conf,  params=None):
        if action == "index":
            return LBGetIndexWorker(task, conf)
        if action == "create":
            return CreateLBWorker(task, conf)
        if action == "delete":
            return DeleteLBWorker(task, conf)
        if action == "show":
            return LBGetDataWorker(task, conf)
        if action == "showDetails":
            return LBshowDetails(task, conf)
        if action == "update":
            return UpdateLBWorker(task, conf)
        if action == "addNode":
            return LBaddNode(task, conf)
        if action == "showNodes":
            return LBShowNodes(task)
        if action == "deleteNode":
            return LBDeleteNode(task, conf)
        if action == "changeNodeStatus":
            return LBChangeNodeStatus(task, conf)
        if action == "updateNode":
            return LBUpdateNode(task, conf)
        if action == "showProbes":
            return LBShowProbes(task, conf)
        if action == "LBAddProbe":
            return LBAddProbe(task, conf)
        if action == "LBdeleteProbe":
            return LBdeleteProbe(task, conf)
        if action == "showSticky":
            return LBShowSticky(task, conf)
        if action == "addSticky":
            return LBAddSticky(task, conf)
        if action == "deleteSticky":
            return LBdeleteSticky(task, conf)
        if action == "findLBforVM":
            return LBFindforVM(task, conf)
