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
import copy

from openstack.common import exception
import balancer.exception as exc

from balancer.core import commands
from balancer.core import lb_status
from balancer.core import scheduler
from balancer import drivers
from balancer.db import api as db_api
from balancer import utils


LOG = logging.getLogger(__name__)


def asynchronous(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        if kwargs.pop('async', True):
            eventlet.spawn(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    return _inner


def lb_get_index(conf, tenant_id):
    lbs = db_api.loadbalancer_get_all_by_project(conf, tenant_id)
    lbs = [db_api.unpack_extra(lb) for lb in lbs]

    for lb in lbs:
        if 'virtualIps' in lb:
            lb.pop('virtualIps')
    return lbs


def lb_find_for_vm(conf, tenant_id, vm_id):
    lbs = db_api.loadbalancer_get_all_by_vm_id(conf, tenant_id, vm_id)
    lbs = [db_api.unpack_extra(lb) for lb in lbs]
    return lbs


def lb_get_data(conf, tenant_id, lb_id):
    LOG.debug("Getting information about loadbalancer with id: %s" % lb_id)
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    lb_dict = db_api.unpack_extra(lb)
    if 'virtualIps' in lb_dict:
        lb_dict.pop("virtualIps")
    LOG.debug("Got information: %s" % list)
    return lb_dict


def lb_show_details(conf, tenant_id, lb_id):
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    vips = db_api.virtualserver_get_all_by_sf_id(conf, sf['id'])
    rs = db_api.server_get_all_by_sf_id(conf, sf['id'])
    probes = db_api.probe_get_all_by_sf_id(conf, sf['id'])
    stickies = db_api.sticky_get_all_by_sf_id(conf, sf['id'])

    lb_ref = db_api.unpack_extra(lb)
    lb_ref['nodes'] = [db_api.unpack_extra(rserver) for rserver in rs]
    lb_ref['virtualIps'] = [db_api.unpack_extra(vip) for vip in vips]
    lb_ref['healthMonitor'] = [db_api.unpack_extra(probe) for probe in probes]
    lb_ref['sessionPersistence'] = [db_api.unpack_extra(sticky)\
            for sticky in stickies]
    return lb_ref


def create_lb(conf, params):
    node_values = params.pop('nodes', [])
    probe_values = params.pop('healthMonitor', [])
    vip_values = params.pop('virtualIps', [])
    lb_values = db_api.loadbalancer_pack_extra(params)

    lb_ref = db_api.loadbalancer_create(conf, lb_values)
    sf_ref = db_api.serverfarm_create(conf, {'lb_id': lb_ref['id']})
    db_api.predictor_create(conf, {'sf_id': sf_ref['id'],
                                   'type': lb_ref['algorithm']})
    vip_update_values = {'protocol': lb_ref['protocol']}

    vips = []
    for vip in vip_values:
        vip = db_api.virtualserver_pack_extra(vip)
        db_api.pack_update(vip, vip_update_values)
        vip['lb_id'] = lb_ref['id']
        vip['sf_id'] = sf_ref['id']
        vips.append(db_api.virtualserver_create(conf, vip))

    servers = []
    for server in node_values:
        server = db_api.server_pack_extra(server)
        server['sf_id'] = sf_ref['id']
        servers.append(db_api.server_create(conf, server))

    probes = []
    for probe in probe_values:
        probe = db_api.probe_pack_extra(probe)
        probe['lb_id'] = lb_ref['id']
        probe['sf_id'] = sf_ref['id']
        probes.append(db_api.probe_create(conf, probe))

    device_ref = scheduler.schedule(conf, lb_ref)
    db_api.loadbalancer_update(conf, lb_ref['id'],
                               {'device_id': device_ref['id']})
    device_driver = drivers.get_device_driver(conf, device_ref['id'])
    with device_driver.request_context() as ctx:
        try:
            commands.create_loadbalancer(ctx, sf_ref, vips, servers, probes,
                                         [])
        except Exception:
            with utils.save_and_reraise_exception():
                db_api.loadbalancer_update(conf, lb_ref['id'],
                                           {'status': lb_status.ERROR,
                                            'deployed': False})
    db_api.loadbalancer_update(conf, lb_ref['id'],
                               {'status': lb_status.ACTIVE,
                                'deployed': True})
    return lb_ref['id']


@asynchronous
def update_lb(conf, tenant_id, lb_id, lb_body):
    lb_ref = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    old_lb_ref = copy.deepcopy(lb_ref)
    db_api.pack_update(lb_ref, lb_body)
    lb_ref = db_api.loadbalancer_update(conf, lb_id, lb_ref)
    if (lb_ref['algorithm'] == old_lb_ref['algorithm'] and
        lb_ref['protocol'] == old_lb_ref['protocol']):
        LOG.debug("In LB %r algorithm and protocol have not changed, "
                     "nothing to do on the device %r.",
                     lb_ref['id'], lb_ref['device_id'])
        return

    sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_ref['id'])[0]
    if lb_ref['algorithm'] != old_lb_ref['algorithm']:
        predictor_ref = db_api.predictor_get_by_sf_id(conf, sf_ref['id'])
        db_api.predictor_update(conf, predictor_ref['id'],
                                {'type': lb_ref['algorithm']})

    vips = db_api.virtualserver_get_all_by_sf_id(conf, sf_ref['id'])
    if lb_ref['protocol'] != old_lb_ref['protocol']:
        vip_update_values = {'protocol': lb_ref['protocol']}
        for vip in vips:
            db_api.pack_update(vip, vip_update_values)
            db_api.virtualserver_update(conf, vip['id'], vip)

    servers = db_api.server_get_all_by_sf_id(conf, sf_ref['id'])
    probes = db_api.probe_get_all_by_sf_id(conf, sf_ref['id'])
    stickies = db_api.sticky_get_all_by_sf_id(conf, sf_ref['id'])

    device_ref = scheduler.reschedule(conf, lb_ref)
    if device_ref['id'] != lb_ref['device_id']:
        from_driver = drivers.get_device_driver(conf, lb_ref['device_id'])
        to_driver = drivers.get_device_driver(conf, device_ref['id'])
        lb_ref = db_api.loadbalancer_update(conf, lb_ref['id'],
                                            {'device_id': device_ref['id']})
    else:
        from_driver = drivers.get_device_driver(conf, device_ref['id'])
        to_driver = from_driver

    with from_driver.request_context() as ctx:
        try:
            commands.delete_loadbalancer(ctx, sf_ref, vips, servers, probes,
                                         stickies)
        except Exception:
            with utils.save_and_reraise_exception():
                db_api.loadbalancer_update(conf, lb_ref['id'],
                                           {'status': lb_status.ERROR})
    with to_driver.request_context() as ctx:
        try:
            commands.create_loadbalancer(ctx, sf_ref, vips, servers, probes,
                                         stickies)
        except Exception:
            with utils.save_and_reraise_exception():
                db_api.loadbalancer_update(conf, lb_ref['id'],
                                           {'status': lb_status.ERROR})
    db_api.loadbalancer_update(conf, lb_ref['id'],
                               {'status': lb_status.ACTIVE})


def delete_lb(conf, tenant_id, lb_id):
    lb_ref = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_ref['id'])[0]
    vips = db_api.virtualserver_get_all_by_sf_id(conf, sf_ref['id'])
    servers = db_api.server_get_all_by_sf_id(conf, sf_ref['id'])
    probes = db_api.probe_get_all_by_sf_id(conf, sf_ref['id'])
    stickies = db_api.sticky_get_all_by_sf_id(conf, sf_ref['id'])
    device_driver = drivers.get_device_driver(conf, lb_ref['device_id'])
    with device_driver.request_context() as ctx:
        commands.delete_loadbalancer(ctx, sf_ref, vips, servers, probes,
                                     stickies)
    db_api.probe_destroy_by_sf_id(conf, sf_ref['id'])
    db_api.sticky_destroy_by_sf_id(conf, sf_ref['id'])
    db_api.server_destroy_by_sf_id(conf, sf_ref['id'])
    db_api.virtualserver_destroy_by_sf_id(conf, sf_ref['id'])
    db_api.predictor_destroy_by_sf_id(conf, sf_ref['id'])
    db_api.serverfarm_destroy(conf, sf_ref['id'])
    db_api.loadbalancer_destroy(conf, lb_ref['id'])


def lb_add_nodes(conf, tenant_id, lb_id, nodes):
    nodes_list = []
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    for node in nodes:
        values = db_api.server_pack_extra(node)
        values['sf_id'] = sf['id']
        if not values['status']:
            values['status'] = 'INSERVICE'
        rs_ref = db_api.server_create(conf, values)
        device_driver = drivers.get_device_driver(conf, lb['device_id'])
        with device_driver.request_context() as ctx:
            commands.add_node_to_loadbalancer(ctx, sf, rs_ref)
        nodes_list.append(db_api.unpack_extra(rs_ref))
    return nodes_list


def lb_show_nodes(conf, tenant_id, lb_id):
    node_list = []
    sf = db_api.serverfarm_get_all_by_lb_id(conf,
            lb_id, tenant_id=tenant_id)[0]
    node_list = map(db_api.unpack_extra,
                    db_api.server_get_all_by_sf_id(conf, sf['id']))
    return node_list


def lb_delete_node(conf, tenant_id, lb_id, lb_node_id):
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    rs = db_api.server_get(conf, lb_node_id)
    db_api.server_destroy(conf, lb_node_id)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_node_from_loadbalancer(ctx, sf, rs)
    return lb_node_id


def lb_change_node_status(conf, tenant_id, lb_id, lb_node_id, lb_node_status):
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    rs = db_api.server_get(conf, lb_node_id)
    sf = db_api.serverfarm_get(conf, rs['sf_id'])
    if rs['state'] == lb_node_status:
        return "OK"

    rs['state'] = lb_node_status
    rsname = rs['name']
    if rs['parent_id'] != "":
        rs['name'] = rs['parent_id']
    LOG.debug("Changing RServer status to: %s" % lb_node_status)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    with device_driver.request_context() as ctx:
        if lb_node_status == "inservice":
            commands.activate_rserver(ctx, sf, rs)
        else:
            commands.suspend_rserver(ctx, sf, rs)

    rs['name'] = rsname
    db_api.server_update(conf, rs['id'], rs)
    return db_api.unpack_extra(rs)


def lb_update_node(conf, tenant_id, lb_id, lb_node_id, lb_node):
    rs = db_api.server_get(conf, lb_node_id, tenant_id=tenant_id)

    lb = db_api.loadbalancer_get(conf, lb_id)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    sf = db_api.serverfarm_get(conf, rs['sf_id'])

    with device_driver.request_context() as ctx:
        commands.delete_rserver_from_server_farm(ctx, sf, rs)
        db_api.pack_update(rs, lb_node)
        new_rs = db_api.server_update(conf, rs['id'], rs)
        commands.add_rserver_to_server_farm(ctx, sf, new_rs)
    return db_api.unpack_extra(new_rs)


def lb_show_probes(conf, tenant_id, lb_id):
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_id,
                tenant_id=tenant_id)[0]
    except IndexError:
        raise exc.ServerFarmNotFound

    probes = db_api.probe_get_all_by_sf_id(conf, sf_ref['id'])

    list = []
    dict = {"healthMonitoring": {}}
    for probe in probes:
        list.append(db_api.unpack_extra(probe))
    dict['healthMonitoring'] = list
    return dict


def lb_add_probe(conf, tenant_id, lb_id, probe_dict):
    LOG.debug("Got new probe description %s" % probe_dict)
    # NOTE(akscram): historically strange validation, wrong place for it.
    if probe_dict['type'] is None:
        return

    lb_ref = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    # NOTE(akscram): server farms are really only create problems than
    #                they solve multiply use of the virtual IPs.
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_ref['id'])[0]
    except IndexError:
        raise exc.ServerFarmNotFound

    values = db_api.probe_pack_extra(probe_dict)
    values['lb_id'] = lb_ref['id']
    values['sf_id'] = sf_ref['id']
    probe_ref = db_api.probe_create(conf, values)
    device_driver = drivers.get_device_driver(conf, lb_ref['device_id'])
    with device_driver.request_context() as ctx:
        commands.add_probe_to_loadbalancer(ctx, sf_ref, probe_ref)
    return db_api.unpack_extra(probe_ref)


def lb_delete_probe(conf, tenant_id, lb_id, probe_id):
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    probe = db_api.probe_get(conf, probe_id)
    db_api.probe_destroy(conf, probe_id)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_probe_from_server_farm(ctx, sf, probe)
    return probe_id


def lb_show_sticky(conf, tenant_id, lb_id):
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_id,
                tenant_id=tenant_id)[0]
    except IndexError:
        raise  exc.ServerFarmNotFound

    stickies = db_api.sticky_get_all_by_sf_id(conf, sf_ref['id'])

    list = []
    dict = {"sessionPersistence": {}}
    for sticky in stickies:
        list.append(db_api.unpack_extra(sticky))
    dict['sessionPersistence'] = list
    return dict


def lb_add_sticky(conf, tenant_id, lb_id, st):
    LOG.debug("Got new sticky description %s" % st)
    if st['type'] is None:
        return
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sf = db_api.serverfarm_get_all_by_lb_id(conf, lb_id)[0]
    values = db_api.sticky_pack_extra(st)
    values['sf_id'] = sf['id']
    sticky_ref = db_api.sticky_create(conf, values)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.add_sticky_to_loadbalancer(ctx, lb, sticky_ref)
    return db_api.unpack_extra(sticky_ref)


def lb_delete_sticky(conf, tenant_id, lb_id, sticky_id):
    lb = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    sticky = db_api.sticky_get(conf, sticky_id)
    device_driver = drivers.get_device_driver(conf, lb['device_id'])
    with device_driver.request_context() as ctx:
        commands.remove_sticky_from_loadbalancer(ctx, lb, sticky)
    db_api.sticky_destroy(conf, sticky_id)
    return sticky_id


def lb_add_vip(conf, tenant_id, lb_id, vip_dict):
    LOG.debug("Called lb_add_vip(), conf: %r, lb_id: %s, vip_dict: %r",
                 conf, lb_id, vip_dict)
    lb_ref = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    # NOTE(akscram): server farms are really only create problems than
    #                they solve multiply use of the virtual IPs.
    try:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(conf, lb_ref['id'])[0]
    except IndexError:
        raise exc.ServerFarmNotFound

    values = db_api.virtualserver_pack_extra(vip_dict)
    values['lb_id'] = lb_ref['id']
    values['sf_id'] = sf_ref['id']
    # XXX(akscram): Set default protocol from LoadBalancer to
    #               VirtualServer if it is not present.
    if not values.get('extra'):
        values['extra'] = {'protocol': lb_ref['protocol']}
    elif 'protocol' not in values['extra']:
        values['extra']['protocol'] = lb_ref['protocol']
    vip_ref = db_api.virtualserver_create(conf, values)
    device_ref = scheduler.reschedule(conf, lb_ref)
    if device_ref['id'] != lb_ref['device_id']:
        update_lb(conf, tenant_id, lb_id, {})
    else:
        device_driver = drivers.get_device_driver(conf, lb_ref['device_id'])
        with device_driver.request_context() as ctx:
            commands.create_vip(ctx, vip_ref, sf_ref)
    return db_api.unpack_extra(vip_ref)


def lb_delete_vip(conf, tenant_id, lb_id, vip_id):
    LOG.debug("Called lb_delete_vip(), conf: %r, lb_id: %s, vip_id: %s",
                 conf, lb_id, vip_id)
    lb_ref = db_api.loadbalancer_get(conf, lb_id, tenant_id=tenant_id)
    vip_ref = db_api.virtualserver_get(conf, vip_id)
    device_driver = drivers.get_device_driver(conf, lb_ref['device_id'])
    with device_driver.request_context() as ctx:
        commands.delete_vip(ctx, vip_ref)
    db_api.virtualserver_destroy(conf, vip_id)


def device_get_index(conf):
    devices = db_api.device_get_all(conf)
    devices = [db_api.unpack_extra(dev) for dev in devices]
    return devices


def device_create(conf, **params):
    device_dict = db_api.device_pack_extra(params)
    device = db_api.device_create(conf, device_dict)
    return device


def device_info(params):
    query = params['query_params']
    LOG.debug("DeviceInfoWorker start with Params: %s Query: %s",
                                                            params, query)
    return


def device_show_algorithms(conf):
    devices = db_api.device_get_all(conf)
    algorithms = []
    for device in devices:
        try:
            device_driver = drivers.get_device_driver(conf, device['id'])
            capabilities = device_driver.get_capabilities()
            if capabilities is not None:
                algorithms += [a for a in capabilities.get('algorithms', [])
                               if a not in algorithms]
        except Exception:
            LOG.warn('Failed to get supported algorithms of device %s',
                     device['name'], exc_info=True)
    return algorithms


def device_show_protocols(conf):
    devices = db_api.device_get_all(conf)
    protocols = []
    for device in devices:
        try:
            device_driver = drivers.get_device_driver(conf, device['id'])
            capabilities = device_driver.get_capabilities()
            if capabilities is not None:
                protocols += [a for a in capabilities.get('protocols', [])
                              if a not in protocols]
        except Exception:
            LOG.warn('Failed to get supported protocols of device %s',
                     device['name'], exc_info=True)
    return protocols


def device_show_vips(conf):
    devices = db_api.device_get_all(conf)
    vips = []
    for device in devices:
        try:
            vips.append(device['extra']['sole_vip'])
        except KeyError:
            pass
    return vips


def device_delete(conf, device_id):
    try:
        lb_refs = db_api.loadbalancer_get_all_by_device_id(conf, device_id)
    except exc.LoadBalancerNotFound:
        db_api.device_destroy(conf, device_id)
        drivers.delete_device_driver(conf, device_id)
        return
    lbs = []
    for lb_ref in lb_refs:
        lb = db_api.unpack_extra(lb_ref)
        lbs.append(lb['id'])
    raise exc.DeviceConflict('Device %s is in use now by loadbalancers %s' %
                             (device_id, ', '.join(lbs)))
