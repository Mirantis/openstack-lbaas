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
from balancer.core import lb_status
from balancer.core import scheduller
from balancer import drivers
from balancer.loadbalancers import vserver
from balancer.db import api as db_api
from balancer import exception as exc


logger = logging.getLogger(__name__)


def asynchronous(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        if kwargs.pop('async', True):
            eventlet.spawn(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    return _inner


def lb_get_index(conf, tenant_id=''):
    lbs = db_api.loadbalancer_get_all_by_project(conf, tenant_id)
    lbs = [db_api.unpack_extra(lb) for lb in lbs]
    return lbs


def lb_find_for_vm(conf, vm_id, tenant_id=''):
    lbs = db_api.loadbalancer_get_all_by_vm_id(conf, vm_id, tenant_id)
    lbs = [db_api.unpack_extra(lb) for lb in lbs]
    return lbs


def lb_get_data(conf, lb_id):
    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    lb = db_api.loadbalancer_get(conf, lb_id)
    logger.debug("Got information: %s" % list)
    return db_api.unpack_extra(lb)


def lb_show_details(conf, lb_id):
    #store = Storage(conf)
    #reader = store.getReader()

    lb = vserver.Balancer(conf)
    lb.loadFromDB(lb_id)

    obj = {'loadbalancer':  db_api.unpack_extra(lb.lb)}
    lbobj = obj['loadbalancer']
    lbobj['nodes'] = [db_api.unpack_extra(v) for v in lb.rs]
    lbobj['virtualIps'] = [db_api.unpack_extra(v) for v in lb.vips]
    lbobj['healthMonitor'] = [db_api.unpack_extra(v) for v in lb.probes]
    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    #list = reader.getLoadvserver.BalancerById(id)
    logger.debug("Got information: %s" % lbobj)
    return lbobj


@asynchronous
def create_lb(conf, **params):
    balancer_instance = vserver.Balancer(conf)

    #Step 1. Parse parameters came from request
    balancer_instance.parseParams(params)
    bal_instance = scheduller.Scheduller.Instance(conf)
    # device = sched.getDevice()
    device = bal_instance.getDeviceByID(balancer_instance.lb['device_id'])

    lb = balancer_instance.getLB()
    lb['device_id'] = device['id']

    #Step 2. Save config in DB
    balancer_instance.savetoDB()

    #Step 3. Deploy config to device
    device_driver = drivers.get_device_driver(conf, device['id'])
    try:
        with device_driver.request_context() as ctx:
            commands.create_loadbalancer(ctx, balancer_instance)
    except (exception.Error, exception.Invalid):
        balancer_instance.lb.status = lb_status.ERROR
    else:
        balancer_instance.lb.status = lb_status.ACTIVE
    balancer_instance.update()

    #balancer_instance.lb.status = \
    #   balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb['id']


@asynchronous
def update_lb(conf, lb_id, lb_body):
    #Step 1. Load LB from DB
    old_balancer_instance = vserver.Balancer(conf)
    balancer_instance = vserver.Balancer(conf)
    logger.debug("Loading LB data from DB for Lb id: %s" % lb_id)
    #TODO add clone function to vserver.Balancer in order to avoid double read
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
#                balancer_instance.sf._predictor =\
#                createPredictor(lb_body[key])
                balancer_instance.sf._predictor = \
                db_api.predictor_pack_extra({'type': lb_body[key]})
            else:
                logger.debug("Got unknown attribute %s of LB. Value is %s"\
                % (key, lb_body[key]))

    #Step 3: Save updated data in DB
    lb.status = lb_status.PENDING_UPDATE
    balancer_instance.update()

    #Step 5. Deploy new config to device
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    try:
        with device_driver.request_context() as ctx:
            commands.update_loadbalancer(ctx, old_balancer_instance,
                    balancer_instance)
    except:
        old_balancer_instance.lb.status = lb_status.ERROR
        old_balancer_instance.update()
        return

    #balancer_instance.lb.status =\
    #    balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb['id']


def delete_lb(conf, lb_id):
    balancer_instance = vserver.Balancer(conf)
    balancer_instance.loadFromDB(lb_id)

    #Step 1. Parse parameters came from request
    #bal_deploy.parseParams(params)

    #        #Step 2. Delete config in DB
    #        balancer_instance.removeFromDB()

    #Step 3. Destruct config at device
    device_id = balancer_instance.lb['device_id']
    device_driver = drivers.get_device_driver(conf, device_id)
    with device_driver.request_context() as ctx:
        commands.delete_loadbalancer(ctx, balancer_instance)

    balancer_instance.removeFromDB()
    return


def lb_add_nodes(conf, lb_id, lb_nodes):
    id_list = []
    balancer_instance = vserver.Balancer(conf)

    for lb_node in lb_nodes:
        logger.debug("Got new node description %s" % lb_node)
        balancer_instance.loadFromDB(lb_id)
        balancer_instance.removeFromDB()

        rs = db_api.server_pack_extra(lb_node)
        rs['sf_id'] = balancer_instance.sf['id']
        rs['name'] = rs['id']

        balancer_instance.rs.append(rs)
        balancer_instance.sf._rservers.append(rs)
        balancer_instance.savetoDB()

        rs = balancer_instance.rs[-1]
        device_driver = drivers.get_device_driver(conf, balancer_instance.\
                                                        lb['device_id'])

        with device_driver.request_context() as ctx:
            commands.add_node_to_loadbalancer(ctx, balancer_instance, rs)

        id_list.append({'id': rs['id']})

    return {'nodes': id_list}


def lb_show_nodes(conf, lb_id):
    balancer_instance = vserver.Balancer(conf)
    nodes = {'nodes': []}
    balancer_instance.loadFromDB(lb_id)
    for rs in balancer_instance.rs:
        rs_dict = db_api.unpack_extra(rs)
        nodes['nodes'].append(rs_dict)
    return nodes


def lb_delete_node(conf, lb_id, lb_node_id):
    balancer_instance = vserver.Balancer(conf)
    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)
    #Step 3: Get RS object from DB
    rs = db_api.server_get(conf, lb_node_id)
    #Step 4: Delete RS from DB
    db_api.server_destroy(conf, lb_node_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(conf,
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_node_from_loadbalancer(ctx, balancer_instance, rs)
    return lb_node_id


def lb_change_node_status(conf, lb_id, lb_node_id, lb_node_status):
    balancer_instance = vserver.Balancer(conf)
    balancer_instance.loadFromDB(lb_id)

    rs = db_api.server_get(conf, lb_node_id)
    sf = balancer_instance.sf
    if rs['state'] == lb_node_status:
        return "OK"

    rs['state'] = lb_node_status
    rsname = rs['name']
    if rs['parent_id'] != "":
        rs['name'] = rs['parent_id']
    logger.debug("Changing RServer status to: %s" % lb_node_status)
    device_driver = drivers.get_device_driver(
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        if lb_node_status == "inservice":
            commands.activate_rserver(ctx, sf, rs)
        else:
            commands.suspend_rserver(ctx, sf, rs)

    rs['name'] = rsname
    db_api.server_update(conf, rs['id'], rs)
    return "Node %s has status %s" % (lb_node_id, rs['state'])


def lb_update_node(conf, lb_id, lb_node_id, lb_node):
    balancer_instance = vserver.Balancer(conf)
    balancer_instance.loadFromDB(lb_id)

    lb_node_dict = db_api.server_pack_extra(lb_node)
    rs = db_api.server_get(conf, lb_node_id)

    new_rs_dict = {}
    new_rs_dict['id'] = rs['id']
    new_rs_dict['extra'] = {}
    if rs['extra']:
        new_rs_dict['extra'].update(rs['extra'])
    for name in rs:
        if name not in ('id', 'extra'):
            new_rs_dict[name] = lb_node_dict.get(name, rs[name])

    db_api.server_destroy(conf, lb_node_id)
    new_rs = db_api.server_create(conf, new_rs_dict)

    device_driver = drivers.get_device_driver(
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_node_from_loadbalancer(ctx, balancer_instance, rs)
        commands.add_node_to_loadbalancer(ctx, balancer_instance, new_rs)
    return "Node with id %s now has params %s" %\
           (lb_node_id, new_rs_dict)


def lb_show_probes(conf, lb_id):
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    except IndexError:
        return exc.ServerFarmNotFound

    probes = db_api.probe_get_all_by_sf_id(conf, sf_ref['id'])

    list = []
    dict = {"healthMonitoring": {}}
    for probe in probes:
        list.append(db_api.unpack_extra(probe))
    dict['healthMonitoring'] = list
    return dict


def lb_add_probe(conf, lb_id, lb_probe):
    logger.debug("Got new probe description %s" % lb_probe)
    if lb_probe['type'] is None:
        return

    balancer_instance = vserver.Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()

    prb = db_api.probe_pack_extra(lb_probe)
    prb['sf_id'] = balancer_instance.sf['id']
    prb['name'] = prb['id']

    balancer_instance.probes.append(prb)
    balancer_instance.sf._probes.append(prb)
    balancer_instance.savetoDB()

    prb = balancer_instance.probes[-1]

    device_driver = drivers.get_device_driver(conf,
                        balancer_instance.lb['device_id'])

    with device_driver.request_context() as ctx:
        commands.add_probe_to_loadbalancer(ctx, balancer_instance, prb)
    return prb['id']


def lb_delete_probe(conf, lb_id, probe_id):
    balancer_instance = vserver.Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)

    #Step 2: Get reader and writer
    #Step 3: Get RS object from DB
    prb = db_api.probe_get(conf, probe_id)

    #Step 4: Delete RS from DB
    db_api.probe_destroy(conf, probe_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(conf,
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_probe_from_server_farm(ctx, balancer_instance, prb)
    return probe_id


def lb_show_sticky(conf, lb_id):
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    except IndexError:
        return  exc.ServerFarmNotFound
    stickies = db_api.sticky_get_all_by_sf_id(conf, sf_ref['id'])

    list = []
    dict = {"sessionPersistence": {}}
    for sticky in stickies:
        list.append(db_api.unpack_extra(sticky))
    dict['sessionPersistence'] = list
    return dict


def lb_add_sticky(conf, lb_id, sticky):
    logger.debug("Got new sticky description %s" % sticky)
    if sticky['persistenceType'] is None:
        return

    balancer_instance = vserver.Balancer(conf)

    balancer_instance.loadFromDB(lb_id)
    balancer_instance.removeFromDB()

    st = db_api.sticky_pack_extra(sticky)
    st['sf_id'] = balancer_instance.sf['id']
    st['name'] = st['id']

    balancer_instance.sf._sticky.append(st)
    balancer_instance.savetoDB()

    st = balancer_instance.sf._sticky[-1]

    device_driver = drivers.get_device_driver(conf,
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.add_sticky_to_loadbalancer(ctx, balancer_instance, st)
    return st['id']


def lb_delete_sticky(conf, lb_id, sticky_id):
    balancer_instance = vserver.Balancer(conf)

    #Step 1: Load balancer from DB
    balancer_instance.loadFromDB(lb_id)

    #Step 2: Get reader and writer
    #Step 3: Get sticky object from DB
    st = db_api.sticky_get(conf, sticky_id)

    #Step 4: Delete sticky from DB
    db_api.sticky_destroy(conf, sticky_id)

    #Step 5: Delete real server from device
    device_driver = drivers.get_device_driver(conf,
                        balancer_instance.lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_sticky_from_loadbalancer(ctx, balancer_instance, st)
    return sticky_id


def device_get_index(conf):
    devices = db_api.device_get_all(conf)
    devices = [db_api.unpack_extra(dev) for dev in devices]
    return devices


def device_create(conf, **params):
    device_dict = db_api.device_pack_extra(params)
    device = db_api.device_create(conf, device_dict)
    scheduller.Scheduller.Instance(conf).addDevice(device)
    return device['id']


def device_info(params):
    query = params['query_params']
    logger.debug("DeviceInfoWorker start with Params: %s Query: %s",
                                                            params, query)
    return


# NOTE(ash): unused func
def device_delete(conf, device_id):
    db_api.device_destroy(conf, device_id)

#    sc = ServiceController.Instance(conf)
#    sched = sc.scheduller
#    sched.addDevice(dev)
    return
