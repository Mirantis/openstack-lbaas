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

from balancer.db import api as db_api

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
            LOG.error("Rollback because of: %s", exc_value)
        rollback_stack = self.context.rollback_stack
        while rollback_stack:
            rollback_stack.pop()(good)
        if not good:
            raise exc_value, exc_type, exc_tb


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
        ctx.device.delete_real_server(rs)
        rs['deployed'] = 'False'
        db_api.server_update(ctx.conf, rs['id'], rs)
        raise


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
                db_api.server_update(rs_child['id'],
                                     {'parent_id': rss[-1]['id']})
            db_api.server_update(rss[-1]['id'],
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
        sf['deployed'] = 'True'
        db_api.serverfarm_update(ctx.conf, sf['id'], sf)
        yield
    except Exception:
        delete_server_farm(ctx, sf)
        raise


@with_rollback
def add_rserver_to_server_farm(ctx, server_farm, rserver):
    try:
        if (rserver.get('parent_id') and rserver['parent_id'] != ""):
            #Nasty hack. We need to think how todo this more elegant
            rserver['name'] = rserver['parent_id']
        ctx.device.add_real_server_to_server_farm(server_farm, rserver)
        yield
    except Exception:
        ctx.device.delete_real_server_from_server_farm(server_farm, rserver)
        raise


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
        probe['deployed'] = 'True'
        db_api.probe_update(ctx.conf, probe['id'], probe)
        yield
    except Exception:
        delete_probe(ctx, probe)
        raise


@with_rollback
def add_probe_to_server_farm(ctx, server_farm, probe):
    try:
        ctx.device.add_probe_to_server_farm(server_farm, probe)
        yield
    except Exception:
        ctx.device.delete_probe_from_server_farm(server_farm, probe)
        raise


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
        vip['deployed'] = 'True'
        db_api.virtualserver_update(ctx.conf, vip['id'], vip)
        yield
    except Exception:
        delete_vip(ctx, vip)
        raise


def create_loadbalancer(ctx, balancer):
    for probe in balancer.probes:
        create_probe(ctx,  probe)
    port = 80
    create_server_farm(ctx, balancer.sf)
    for rserver in balancer.rs:
        create_rserver(ctx, rserver)
        add_rserver_to_server_farm(ctx, balancer.sf, rserver)
        port = rserver['port']
    for probe in balancer.probes:
        probe['port'] = port
        create_probe(ctx,  probe)
        add_probe_to_server_farm(ctx, balancer.sf, probe)
    for vip in balancer.vips:
        create_vip(ctx, vip, balancer.sf)


def delete_loadbalancer(ctx, balancer):
    for vip in balancer.vips:
        delete_vip(ctx, vip)
#    for pr in balancer.probes:
#        DeleteProbeFromSFCommand(driver,  context,  balancer.sf,  pr)
#        DeleteProbeCommand(driver,  context,  pr)
    for rserver in balancer.rs:
        delete_rserver_from_server_farm(ctx, balancer.sf, rserver)
        delete_rserver(ctx, rserver)
    for probe in balancer.probes:
        remove_probe_from_server_farm(ctx, balancer.sf, probe)
        delete_probe(ctx, probe)
    for sticky in balancer.sf._sticky:
        delete_sticky(ctx, sticky)
    delete_server_farm(ctx, balancer.sf)


def update_loadbalancer(ctx, old_algo, new_algo, sf):
    if old_algo != new_algo:
        for s in sf:
            create_server_farm(ctx, s)


def add_node_to_loadbalancer(ctx, balancer, rserver):
    create_rserver(ctx, rserver)
    add_rserver_to_server_farm(ctx, balancer.sf, rserver)


def remove_node_from_loadbalancer(ctx, balancer, rserver):
    delete_rserver_from_server_farm(ctx, balancer.sf, rserver)
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
