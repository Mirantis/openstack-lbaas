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
import functools
import eventlet

from balancer.core.scheduller import Scheduller
from balancer.devices.DeviceMap import DeviceMap
from balancer.loadbalancers.realserver import RealServer
from balancer.loadbalancers.vserver import Balancer, Deployer, Destructor
from balancer.loadbalancers.vserver import makeDeleteLBCommandChain,\
                                           makeDeleteStickyFromLBChain,\
                                           makeAddStickyToLBChain,\
                                           makeDeleteProbeFromLBChain,\
                                           makeAddProbeToLBChain,\
                                           makeDeleteNodeFromLBChain,\
                                           makeAddNodeToLBChain
from balancer.loadbalancers.vserver import createSticky, createProbe,\
                                           createPredictor
from balancer.loadbalancers.vserver import SuspendRServerCommand,\
                                           ActivateRServerCommand
from balancer.processing.processing import Processing
from balancer.storage.storage import Storage

logger = logging.getLogger(__name__)

def asynchronous(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        if kwargs.pop('async', True):
            eventlet.spawn(func, args, kwargs)
        else:
            return func(*args, **kwargs)

    return _inner

def lb_get_index(conf, tenant_id=''):
    store = Storage(conf)
    reader = store.getReader()
    return reader.getLoadBalancers(tenant_id)

def lb_find_for_vm(conf, vm_id, tenant_id=''):
    store = Storage(conf)
    reader = store.getReader()
    return reader.getLoadBalancersByVMid(vm_id,  tenant_id)

def lb_get_data(conf, lb_id):
    store = Storage(conf)
    reader = store.getReader()

    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    list = reader.getLoadBalancerById(lb_id)
    logger.debug("Got information: %s" % list)
    return list

def lb_show_details(conf, lb_id):
    store = Storage(conf)
    #reader = store.getReader()

    lb = Balancer(conf)
    lb.loadFromDB(lb_id)
    obj = {'loadbalancer':  lb.lb.convertToDict()}
    lbobj = obj['loadbalancer']
    lbobj['nodes'] = lb.rs
    lbobj['virtualIps'] = lb.vips
    lbobj['healthMonitor'] = lb.probes
    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    #list = reader.getLoadBalancerById(id)
    logger.debug("Got information: %s" % lbobj)
    return lbobj

@asynchronous
def create_lb(conf, **params):
    balancer_instance = Balancer(conf)

    #Step 1. Parse parameters came from request
    balancer_instance.parseParams(params)
    bal_instance = Scheduller.Instance(conf)
    # device = sched.getDevice()
    device = bal_instance.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    lb = balancer_instance.getLB()
    lb.device_id = device.id

    #Step 2. Save config in DB
    balancer_instance.savetoDB()

    #Step 3. Deploy config to device
    commands = makeCreateLBCommandChain(balancer_instance,  driver, \
    context, conf)
    context.addParam('balancer',  balancer_instance)
    deploy = Deployer(device,  context)
    deploy.commands = commands
    processing = Processing.Instance(conf)
    event = balancer.processing.event.Event(balancer.processing.event.\
                                                                EVENT_PROCESS,
                                                                deploy,  2)
    try:
        processing.put_event(event)
        
    except openstack.common.exception.Error:
        balancer_instance.lb.status = \
            balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
        balancer_instance.update()
        return
    except openstack.common.exception.Invalid:
        balancer_instance.lb.status = \
            balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
        balancer_instance.update()
        return

    #balancer_instance.lb.status = \
    #   balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb.id

@asynchronous
def update_lb(conf, lb_id, lb_body):
    sched = Scheduller.Instance(conf)

    #Step 1. Load LB from DB
    old_balancer_instance = Balancer(conf)
    balancer_instance = Balancer(conf)
    logger.debug("Loading LB data from DB for Lb id: %s" % lb_id)
    #TODO add clone function to Balancer in order to avoid double read
    balancer_instance.loadFromDB(lb_id)
    old_balancer_instance.loadFromDB(lb_id)

    #Step 2. Parse parameters came from request
    lb = balancer_instance.lb
    old_predictor_id = None
    port_updated = False
    for key in lb_body.keys():
        if hasattr(lb, key):
            logger.debug("updating attribute %s of LB. Value is %s"\
            % (key, lb_body[key]))
            setattr(lb, key, lb_body[key])
            if key.lower() == "algorithm":
                old_predictor_id = balancer_instance.sf._predictor.id
                balancer_instance.sf._predictor =\
                createPredictor(lb_body[key])
            else:
                logger.debug("Got unknown attribute %s of LB. Value is %s"\
                % (key, lb_body[key]))

    #Step 3: Save updated data in DB
    lb.status =\
    balancer.loadbalancers.loadbalancer.LB_PENDING_UPDATE_STATUS
    balancer_instance.update()

    #Step 4. Update device config
    device = sched.getDeviceByID(lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    #Step 5. Deploy new config to device
    commands = makeUpdateLBCommandChain(old_balancer_instance,\
        balancer_instance,  driver,  context, conf)
    deploy = Deployer()
    deploy.commands = commands
    try:
        deploy.execute()
    except:
        old_balancer_instance.lb.status =\
        balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
        old_balancer_instance.update()
        return

    #balancer_instance.lb.status =\
    #    balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb.id

def delete_lb(conf, lb_id):
    sched = Scheduller.Instance(conf)
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)

    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    #Step 1. Parse parameters came from request
    #bal_deploy.parseParams(params)

    #        #Step 2. Delete config in DB
    #        balancer_instance.removeFromDB()

    #Step 3. Destruct config at device
    commands = makeDeleteLBCommandChain(balancer_instance,\
        driver,  context, conf)
    destruct = Destructor()
    destruct.commands = commands
    destruct.execute()

    balancer_instance.removeFromDB()
    return

def lb_add_node(conf, lb_id, lb_node):
    logger.debug("Got new node description %s" % lb_node)
    rs = RealServer()
    sched = Scheduller.Instance(conf)
    balancer_instance = Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()
    rs.loadFromDict(lb_node)
    rs.sf_id = balancer_instance.sf.id
    rs.name = rs.id

    balancer_instance.rs.append(rs)
    balancer_instance.sf._rservers.append(rs)
    balancer_instance.savetoDB()

    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    commands = makeAddNodeToLBChain(balancer_instance, driver, context, rs, conf)
    deploy = Deployer()
    deploy.commands = commands
    deploy.execute()
    return  rs.id

def lb_show_nodes (conf, lb_id):
    balancer_instance = Balancer(conf)
    nodes = {'nodes': []}

    balancer_instance.loadFromDB(lb_id)
    for rs in balancer_instance.rs:
        nodes['nodes'].append(rs.convertToDict())
    return nodes

def lb_delete_node(conf, lb_id, lb_node_id):
    balancer_instance = Balancer(conf)
    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)
    sched = Scheduller.Instance(conf)
    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)
    store = Storage(conf)

    #Step 2: Get reader and writer
    rd = store.getReader()
    dl = store.getDeleter()
    #Step 3: Get RS object from DB
    rs = rd.getRServerById(lb_node_id)

    #Step 4: Delete RS from DB
    dl.deleteRSbyID(lb_node_id)

    #Step 5: Make commands for deleting RS

    commands = makeDeleteNodeFromLBChain(balancer_instance, driver, context, rs, conf)
    destruct = Destructor()
    destruct.commands = commands

    #Step 6: Delete real server from device
    destruct.execute()
    return lb_node_id

def lb_change_node_status(conf, lb_id, lb_node_id, lb_node_status):
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)
    sched = Scheduller.Instance(conf)
    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)
    store = Storage(conf)
    reader = store.getReader()
    writer = store.getWriter()
    deleter = store.getDeleter()

    rs = reader.getRServerById(lb_node_id)
    sf = balancer_instance.sf
    if rs.state == nodeStatus:
        return "OK"

    commands =[]
    rs.state = lb_node_status
    rsname = rs.name
    if rs.parent_id !="":
        rs.name = rs.parent_id
    logger.debug("Changing RServer status to: %s" % lb_node_status)
    if lb_node_status == "inservice":
        commands.append(ActivateRServerCommand(driver,  context, sf, rs))
    else:
        commands.append(SuspendRServerCommand(driver,  context, sf, rs))

    deploy = Deployer()

    deploy.commands = commands
    deploy.execute()
    rs.name = rsname
    writer.updateObjectInTable(rs)
    return "Node %s has status %s" % (nodeID, rs.state)

def lb_update_node(conf, lb_id, lb_node_id, lb_node):
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)
    sched = Scheduller.Instance(conf)
    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)
    store = Storage(conf)
    reader = store.getReader()
    writer = store.getWriter()
    deleter = store.getDeleter()

    rs = reader.getRServerById(lb_node_id)
    dict = rs.convertToDict()
    new_rs = RealServer()
    new_rs.loadFromDict(dict)

    for prop in lb_node.keys():
        if hasattr(rs, prop):
            if dict[prop] != lb_node[prop]:
                setattr(new_rs, prop, lb_node[prop])

    deleter.deleteRSbyID(nodeID)
    writer.writeRServer(new_rs)
    deploy = Deployer()
    commands =\
    makeDeleteNodeFromLBChain(balancer_instance, driver, context,  rs, conf)\
    + makeAddNodeToLBChain(balancer_instance, driver, context, new_rs, conf)
    deploy.commands = commands
    deploy.execute()
    return "Node with id %s now has params %s" %\
           (lb_node_id, new_rs.convertToDict())

def lb_show_probes(conf, lb_id):
    store = Storage(conf)
    reader = store.getReader()

    sf_id = reader.getSFByLBid(lb_id).id
    probes = reader.getProbesBySFid(sf_id)

    list = []
    dict = {"healthMonitoring": {}}
    for prb in probes:
        list.append(prb.convertToDict())
    dict['healthMonitoring'] = list
    return dict

def lb_add_probe(conf, lb_id, lb_probe):
    logger.debug("Got new probe description %s" % lb_probe)
    if lb_probe['type'] == None:
        return

    scheduller = Scheduller.Instance(conf)
    balancer_instance = Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()
    prb = createProbe(lb_probe['type'])
    prb.loadFromDict(lb_probe)
    prb.sf_id = balancer_instance.sf.id
    prb.name = prb.id

    balancer_instance.probes.append(prb)
    balancer_instance.sf._probes.append(prb)
    balancer_instance.savetoDB()

    device = scheduller.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    commands = makeAddProbeToLBChain(balancer_instance, driver, context, prb, conf)
    deploy = Deployer()
    deploy.commands = commands
    deploy.execute()
    return prb.id

def lb_delete_probe(conf, lb_id, probe_id):
    balancer_instance = Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)
    scheduller = Scheduller.Instance(conf)
    device = scheduller.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    store = Storage(conf)

    #Step 2: Get reader and writer
    rd = store.getReader()
    dl = store.getDeleter()

    #Step 3: Get RS object from DB
    prb = rd.getProbeById(probe_id)

    #Step 4: Delete RS from DB
    dl.deleteProbeByID(probe_id)

    #Step 5: Make commands for deleting probe
    commands =\
    makeDeleteProbeFromLBChain(balancer_instance, driver, context, prb, conf)
    destruct = Destructor()
    destruct.commands = commands

    #Step 6: Delete real server from device
    destruct.execute()
    return probe_id

def lb_show_sticky(conf, lb_id):
    store = Storage(conf)
    reader = store.getReader()

    sf_id = reader.getSFByLBid(lb_id).id
    stickies = reader.getStickiesBySFid(sf_id)

    list = []
    dict = {"sessionPersistence": {}}
    for st in stickies:
        list.append(st.convertToDict())
    dict['sessionPersistence'] = list
    return dict

def lb_add_sticky(conf, lb_id, sticky):
    logger.debug("Got new sticky description %s" % sticky)
    if sticky['type'] == None:
        return

    sched = Scheduller(conf)
    balancer_instance = Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()
    st = createSticky(sticky['type'])
    st.loadFromDict(sticky)
    st.sf_id = balancer_instance.sf.id
    st.name = st.id

    balancer_instance.sf._sticky.append(st)
    balancer_instance.savetoDB()

    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    commands = makeAddStickyToLBChain(balancer_instance, driver, context, st,
                                                                          conf)
    deploy = Deployer()
    deploy.commands = commands
    deploy.execute()
    return st.id

def lb_delete_sticky(conf, lb_id, sticky_id):
    balancer_instance = Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)
    sched = Scheduller(conf)
    device = sched.getDeviceByID(balancer_instance.lb.device_id)
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
    commands =\
    makeDeleteStickyFromLBChain(balancer_instance, driver, context, st,
                                                                    conf)
    destruct = Destructor()
    destruct.commands = commands

    #Step 6: Delete real server from device
    destruct.execute()
    return sticky_id