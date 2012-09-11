# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools
import logging
import types

import balancer.db.api as db_api
from balancer import utils

LOG = logging.getLogger(__name__)


class RollbackContext(object):
    def __init__(self):
        self.rollback_stack = []

    def add_rollback(self, rollback):
        self.rollback_stack.append(rollback)


class RollbackContextManager(object):
    def __init__(self, context=None):
        if context is None:
            self.context = RollbackContext()
        else:
            self.context = context

    def __enter__(self):
        return self.context

    def __exit__(self, exc_type, exc_value, exc_tb):
        good = exc_type is None
        if not good:
            LOG.error("Rollback because of: %s", exc_value,
                    exc_info=(exc_value, exc_type, exc_tb))
        rollback_stack = self.context.rollback_stack
        while rollback_stack:
            rollback_stack.pop()(good)
        if not good:
            raise exc_type, exc_value, exc_tb


class Rollback(Exception):
    pass


def with_rollback(func):
    @functools.wraps(func)
    def __inner(ctx, *args, **kwargs):
        gen = func(ctx, *args, **kwargs)
        if not isinstance(gen, types.GeneratorType):
            LOG.critical("Expected generator, got %r instead", gen)
            raise RuntimeError(
                    "Commands with rollback must be generator functions")
        try:
            res = gen.next()
        except StopIteration:
            LOG.warn("Command %s finished w/o yielding", func.__name__)
        else:
            def fin(good):
                if good:
                    gen.close()
                else:
                    try:
                        gen.throw(Rollback)
                    except Rollback:
                        pass
                    except Exception:
                        LOG.exception("Exception during rollback.")
            ctx.add_rollback(fin)
        return res
    return __inner


def ignore_exceptions(func):
    @functools.wraps(func)
    def __inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            LOG.exception("Got exception while executing %s. Ignored.",
                                                                 func.__name__)
    return __inner


@with_rollback
def create_rserver(ctx, rs):
    try:
        # We can't create multiple RS with the same IP. So parent_id points to
        # RS which already deployed and has this IP
        LOG.debug("Creating rserver command execution with rserver: %s", rs)
        LOG.debug("RServer parent_id: %s", rs['parent_id'])
        if not rs['parent_id']:
            ctx.device.create_real_server(rs)
            rs['deployed'] = 'True'
            db_api.server_update(ctx.conf, rs['id'], rs)
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            ctx.device.delete_real_server(rs)
            rs['deployed'] = 'False'
            db_api.server_update(ctx.conf, rs['id'], rs)


@ignore_exceptions
def delete_rserver(ctx, rs):
    rss = []
    LOG.debug("Got delete RS request")
    if rs['parent_id'] == "":
        rss = db_api.server_get_all_by_parent_id(ctx.conf, rs['id'])
        LOG.debug("List of servers: %s", rss)
        ctx.device.delete_real_server(rs)
        if len(rss) > 0:
            for rs_child in rss:
                db_api.server_update(ctx.conf, rs_child['id'],
                                     {'parent_id': rss[-1]['id']})
            db_api.server_update(ctx.conf, rss[-1]['id'],
                                     {'parent_id': '', 'deployed': 'True'})
            ctx.device.create_real_server(rss[-1])


def create_sticky(ctx, sticky):
    ctx.device.create_stickiness(sticky)
    sticky['deployed'] = 'True'
    db_api.sticky_update(ctx.conf, sticky['id'], sticky)


@ignore_exceptions
def delete_sticky(ctx, sticky):
    ctx.device.delete_stickiness(sticky)
    sticky['deployed'] = 'False'
    db_api.sticky_update(ctx.conf, sticky['id'], sticky)


@ignore_exceptions
def delete_server_farm(ctx, sf):
    ctx.device.delete_server_farm(sf)
    sf['deployed'] = 'False'
    db_api.serverfarm_update(ctx.conf, sf['id'], sf)


@with_rollback
def create_server_farm(ctx, sf):
    try:
        pr = db_api.predictor_get_all_by_sf_id(ctx.conf, sf['id'])
        ctx.device.create_server_farm(sf, pr)
        db_api.serverfarm_update(ctx.conf, sf['id'], {'deployed': True})
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            delete_server_farm(ctx, sf)


@with_rollback
def add_rserver_to_server_farm(ctx, server_farm, rserver):
    try:
        if (rserver.get('parent_id') and rserver['parent_id'] != ""):
            #Nasty hack. We need to think how todo this more elegant
            rserver['name'] = rserver['parent_id']
        ctx.device.add_real_server_to_server_farm(server_farm, rserver)
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            ctx.device.delete_real_server_from_server_farm(server_farm,
                    rserver)


@ignore_exceptions
def delete_rserver_from_server_farm(ctx, server_farm, rserver):
    ctx.device.delete_real_server_from_server_farm(server_farm, rserver)


@ignore_exceptions
def delete_probe(ctx, probe):
    ctx.device.delete_probe(probe)
    probe['deployed'] = 'False'
    db_api.probe_update(ctx.conf, probe['id'], probe)


@with_rollback
def create_probe(ctx, probe):
    try:
        ctx.device.create_probe(probe)
        db_api.probe_update(ctx.conf, probe['id'], {'deployed': True})
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            delete_probe(ctx, probe)


@with_rollback
def add_probe_to_server_farm(ctx, server_farm, probe):
    try:
        ctx.device.add_probe_to_server_farm(server_farm, probe)
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            ctx.device.delete_probe_from_server_farm(server_farm, probe)


@ignore_exceptions
def remove_probe_from_server_farm(ctx, server_farm, probe):
    ctx.device.delete_probe_from_server_farm(server_farm, probe)


def activate_rserver(ctx, server_farm, rserver):
    ctx.device.activate_real_server(server_farm, rserver)


def suspend_rserver(ctx, server_farm, rserver):
    ctx.device.suspend_real_server(server_farm, rserver)


@ignore_exceptions
def delete_vip(ctx, vip):
    ctx.device.delete_virtual_ip(vip)
    vip['deployed'] = 'False'
    db_api.virtualserver_update(ctx.conf, vip['id'], vip)


@with_rollback
def create_vip(ctx, vip, server_farm):
    try:
        ctx.device.create_virtual_ip(vip, server_farm)
        db_api.virtualserver_update(ctx.conf, vip['id'], {'deployed': True})
        yield
    except Exception:
        with utils.save_and_reraise_exception():
            delete_vip(ctx, vip)


def create_loadbalancer(ctx, balancer, nodes, probes, vips):
    lb = db_api.unpack_extra(balancer)
    sf = db_api.serverfarm_create(ctx.conf, {'lb_id': lb['id']})
    if 'algorithm' in lb:
        predictor_params = {'sf_id': sf['id'], 'type': lb['algorithm']}
    else:
        predictor_params = {'sf_id': sf['id']}
    db_api.predictor_create(ctx.conf, predictor_params)
    create_server_farm(ctx, sf)
    for node in nodes:
        node_values = db_api.server_pack_extra(node)
        node_values['sf_id'] = sf['id']
        rs_ref = db_api.server_create(ctx.conf, node_values)
        create_rserver(ctx, rs_ref)
        add_rserver_to_server_farm(ctx, sf, rs_ref)

    for probe in probes:
        probe_values = db_api.probe_pack_extra(probe)
        probe_values['lb_id'] = lb['id']
        probe_values['sf_id'] = sf['id']
        probe_ref = db_api.probe_create(ctx.conf, probe_values)
        create_probe(ctx,  probe_ref)
        add_probe_to_server_farm(ctx, sf, probe_ref)

    for vip in vips:
        vip_values = db_api.virtualserver_pack_extra(vip)
        vip_values['lb_id'] = lb['id']
        vip_values['sf_id'] = sf['id']
        if not vip_values.get('extra'):
            vip_values['extra'] = {'protocol': lb['protocol']}
        elif 'protocol' not in vip_values['extra']:
            vip_values['extra']['protocol'] = lb['protocol']
        vip_ref = db_api.virtualserver_create(ctx.conf, vip_values)
        create_vip(ctx, vip_ref, sf)


def delete_loadbalancer(ctx, lb):
    sf = db_api.serverfarm_get_all_by_lb_id(ctx.conf, lb['id'])[0]
    vips = db_api.virtualserver_get_all_by_sf_id(ctx.conf, sf['id'])
    rs = db_api.server_get_all_by_sf_id(ctx.conf, sf['id'])
    probes = db_api.probe_get_all_by_sf_id(ctx.conf, sf['id'])
    stickies = db_api.sticky_get_all_by_sf_id(ctx.conf, sf['id'])
    for vip in vips:
        delete_vip(ctx, vip)
    for rserver in rs:
        delete_rserver_from_server_farm(ctx, sf, rserver)
        delete_rserver(ctx, rserver)
    for probe in probes:
        remove_probe_from_server_farm(ctx, sf, probe)
        delete_probe(ctx, probe)
    for sticky in stickies:
        delete_sticky(ctx, sticky)
    delete_server_farm(ctx, sf)
    db_api.predictor_destroy_by_sf_id(ctx.conf, sf['id'])
    db_api.server_destroy_by_sf_id(ctx.conf, sf['id'])
    db_api.probe_destroy_by_sf_id(ctx.conf, sf['id'])
    db_api.virtualserver_destroy_by_sf_id(ctx.conf, sf['id'])
    db_api.sticky_destroy_by_sf_id(ctx.conf, sf['id'])
    db_api.serverfarm_destroy(ctx.conf, sf['id'])
    db_api.loadbalancer_destroy(ctx.conf, lb['id'])


def update_loadbalancer(ctx, old_bal_ref,  new_bal_ref):
    if old_bal_ref['algorithm'] != new_bal_ref['algorithm']:
        sf_ref = db_api.serverfarm_get_all_by_lb_id(ctx.conf,
                                                    new_bal_ref['id'])[0]
        create_server_farm(ctx, sf_ref)


def add_node_to_loadbalancer(ctx, sf, rserver):
    create_rserver(ctx, rserver)
    add_rserver_to_server_farm(ctx, sf, rserver)


def remove_node_from_loadbalancer(ctx, sf, rserver):
    delete_rserver_from_server_farm(ctx, sf, rserver)
    delete_rserver(ctx, rserver)


def add_probe_to_loadbalancer(ctx, sf_ref, probe_ref):
    create_probe(ctx, probe_ref)
    add_probe_to_server_farm(ctx, sf_ref, probe_ref)


def makeDeleteProbeFromLBChain(ctx, balancer, probe):
    remove_probe_from_server_farm(ctx, balancer.sf, probe)
    delete_probe(ctx, probe)


def add_sticky_to_loadbalancer(ctx, balancer, sticky):
    create_sticky(ctx, sticky)


def remove_sticky_from_loadbalancer(ctx, balancer, sticky):
    delete_sticky(ctx, sticky)
