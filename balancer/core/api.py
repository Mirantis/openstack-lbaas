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

from openstack.common import exception

from balancer.core import commands
from balancer.core.scheduller import Scheduller
from balancer import drivers
from balancer.devices.device import LBDevice
from balancer.core.ServiceController import ServiceController
from balancer.loadbalancers import loadbalancer
from balancer.loadbalancers.realserver import RealServer
from balancer.loadbalancers.vserver import Balancer
from balancer.loadbalancers.vserver import createSticky, createProbe,\
                                           createPredictor
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
    #store = Storage(conf)
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

    lb = balancer_instance.getLB()
    lb.device_id = device.id

    #Step 2. Save config in DB
    balancer_instance.savetoDB()

    #Step 3. Deploy config to device
    device_driver = drivers.get_device_driver(device.id)
    try:
        with device_driver.request_context() as ctx:
            commands.create_loadbalancer(ctx, balancer_instance)
    except (exception.Error, exception.Invalid):
        balancer_instance.lb.status = loadbalancer.LB_ERROR_STATUS
    else:
        balancer_instance.lb.status = loadbalancer.LB_ACTIVE_STATUS
    balancer_instance.update()

    #balancer_instance.lb.status = \
    #   balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb.id


@asynchronous
def update_lb(conf, lb_id, lb_body):
    #Step 1. Load LB from DB
    old_balancer_instance = Balancer(conf)
    balancer_instance = Balancer(conf)
    logger.debug("Loading LB data from DB for Lb id: %s" % lb_id)
    #TODO add clone function to Balancer in order to avoid double read
    balancer_instance.loadFromDB(lb_id)
    old_balancer_instance.loadFromDB(lb_id)

    #Step 2. Parse parameters came from request
    lb = balancer_instance.lb
    #old_predictor_id = None
    #port_updated = False
    for key in lb_body.keys():
        if hasattr(lb, key):
            logger.debug("updating attribute %s of LB. Value is %s"\
            % (key, lb_body[key]))
            setattr(lb, key, lb_body[key])
            if key.lower() == "algorithm":
                #old_predictor_id = balancer_instance.sf._predictor.id
                balancer_instance.sf._predictor =\
                createPredictor(lb_body[key])
            else:
                logger.debug("Got unknown attribute %s of LB. Value is %s"\
                % (key, lb_body[key]))

    #Step 3: Save updated data in DB
    lb.status = loadbalancer.LB_PENDING_UPDATE_STATUS
    balancer_instance.update()

    #Step 5. Deploy new config to device
    device_driver = drivers.get_device_driver(lb.device_id)
    try:
        with device_driver.request_context() as ctx:
            commands.update_loadbalancer(ctx, old_balancer_instance,
                    balancer_instance)
    except:
        old_balancer_instance.lb.status = loadbalancer.LB_ERROR_STATUS
        old_balancer_instance.update()
        return

    #balancer_instance.lb.status =\
    #    balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb.id


def delete_lb(conf, lb_id):
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)

    #Step 1. Parse parameters came from request
    #bal_deploy.parseParams(params)

    #        #Step 2. Delete config in DB
    #        balancer_instance.removeFromDB()

    #Step 3. Destruct config at device
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.delete_loadbalancer(ctx, balancer_instance)

    balancer_instance.removeFromDB()
    return


def lb_add_node(conf, lb_id, lb_node):
    logger.debug("Got new node description %s" % lb_node)
    rs = RealServer()
    balancer_instance = Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()
    rs.loadFromDict(lb_node)
    rs.sf_id = balancer_instance.sf.id
    rs.name = rs.id

    balancer_instance.rs.append(rs)
    balancer_instance.sf._rservers.append(rs)
    balancer_instance.savetoDB()

    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.delete_loadbalancer(ctx, balancer_instance)
        commands.add_node_to_loadbalancer(ctx, balancer_instance, rs)

    return  rs.id


def lb_show_nodes(conf, lb_id):
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
    store = Storage(conf)

    #Step 2: Get reader and writer
    rd = store.getReader()
    dl = store.getDeleter()
    #Step 3: Get RS object from DB
    rs = rd.getRServerById(lb_node_id)

    #Step 4: Delete RS from DB
    dl.deleteRSbyID(lb_node_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.remove_node_from_loadbalancer(ctx, balancer_instance, rs)
    return lb_node_id


def lb_change_node_status(conf, lb_id, lb_node_id, lb_node_status):
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)
    store = Storage(conf)
    reader = store.getReader()
    writer = store.getWriter()
    #deleter = store.getDeleter()

    rs = reader.getRServerById(lb_node_id)
    sf = balancer_instance.sf
    if rs.state == lb_node_status:
        return "OK"

    rs.state = lb_node_status
    rsname = rs.name
    if rs.parent_id != "":
        rs.name = rs.parent_id
    logger.debug("Changing RServer status to: %s" % lb_node_status)
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        if lb_node_status == "inservice":
            commands.activate_rserver(ctx, sf, rs)
        else:
            commands.suspend_rserver(ctx, sf, rs)

    rs.name = rsname
    writer.updateObjectInTable(rs)
    return "Node %s has status %s" % (lb_node_id, rs.state)


def lb_update_node(conf, lb_id, lb_node_id, lb_node):
    balancer_instance = Balancer(conf)
    balancer_instance.loadFromDB(lb_id)
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

    deleter.deleteRSbyID(lb_node_id)
    writer.writeRServer(new_rs)
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.remove_node_from_loadbalancer(ctx, balancer_instance, rs)
        commands.add_node_to_loadbalancer(ctx, balancer_instance, rs)
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

    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.add_probe_to_loadbalancer(ctx, balancer_instance, prb)

    return prb.id


def lb_delete_probe(conf, lb_id, probe_id):
    balancer_instance = Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)

    store = Storage(conf)

    #Step 2: Get reader and writer
    rd = store.getReader()
    dl = store.getDeleter()

    #Step 3: Get RS object from DB
    prb = rd.getProbeById(probe_id)

    #Step 4: Delete RS from DB
    dl.deleteProbeByID(probe_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.remove_probe_from_server_farm(ctx, balancer_instance, prb)
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

    balancer_instance = Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()
    st = createSticky(sticky['type'])
    st.loadFromDict(sticky)
    st.sf_id = balancer_instance.sf.id
    st.name = st.id

    balancer_instance.sf._sticky.append(st)
    balancer_instance.savetoDB()

    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.add_sticky_to_loadbalancer(ctx, balancer_instance, st)

    return st.id


def lb_delete_sticky(conf, lb_id, sticky_id):
    balancer_instance = Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)
    store = Storage(conf)

    #Step 2: Get reader and writer
    rd = store.getReader()
    dl = store.getDeleter()

    #Step 3: Get sticky object from DB
    st = rd.getStickyById(sticky_id)

    #Step 4: Delete sticky from DB
    dl.deleteStickyByID(sticky_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(balancer_instance.lb.device_id)
    with device_driver.request_context() as ctx:
        commands.remove_sticky_from_loadbalancer(ctx, balancer_instance, st)

    return sticky_id


def device_get_index(conf):
    store = Storage(conf)
    reader = store.getReader()
    list = reader.getDevices()
    return list


def device_create(conf, **params):
    device = LBDevice()
    device.loadFromDict(params)

    store = Storage(conf)
    writer = store.getWriter()
    writer.writeDevice(device)
    sc = ServiceController.Instance(conf)
    sched = sc.scheduller
    sched.addDevice(device)
    return 'OK'


def device_info(params):
    query = params['query_params']
    logger.debug("DeviceInfoWorker start with Params: %s Query: %s",
                                                                params, query)
    return


def device_delete(conf, **params):
    dev = LBDevice()
    dev.loadFromDict(params)

    store = Storage(conf)
    writer = store.getWriter()
    writer.writeDevice(dev)
    sc = ServiceController.Instance(conf)
    sched = sc.scheduller
    sched.addDevice(dev)
    return
