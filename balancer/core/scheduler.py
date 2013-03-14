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

from balancer.db import api as db_api
from balancer import exception as exp
from balancer.common import cfg, utils
from balancer import drivers

LOG = logging.getLogger(__name__)

bind_opts = [
    cfg.ListOpt('device_filters',
        default=['balancer.core.scheduler.filter_capabilities']),
    cfg.ListOpt('device_cost_functions',
        default=['balancer.core.scheduler.lbs_on']),
]


def _process_config(conf):
    conf.register_opts(bind_opts)
    device_filters = [utils.import_class(foo) for foo in conf.device_filters]
    cost_functions = []
    for fullname in conf.device_cost_functions:
        conf_name = 'device_cost_%s_weight' % fullname.rpartition('.')[-1]
        try:
            weight = getattr(conf, conf_name)
        except cfg.NoSuchOptError:
            conf.register_opt(cfg.FloatOpt(conf_name, default=1.))
            weight = getattr(conf, conf_name)
        cost_functions.append((utils.import_class(fullname), weight))
    return device_filters, cost_functions


def _filter_devices(conf, lb_ref, devices, filters):
    filtered_devices = [device_ref for device_ref in devices
                            if all(filter(conf, lb_ref, device_ref)
                                   for filter in filters)]
    if not filtered_devices:
        raise exp.NoValidDevice
    return filtered_devices


def _weight_devices(conf, lb_ref, devices, cost_functions):
    weighted = []
    for device_ref in devices:
        weight = 0.0
        for cost_func, cost_weight in cost_functions:
            weight += cost_weight * cost_func(conf, lb_ref, device_ref)
        weighted.append((weight, device_ref))
    weighted.sort()
    return weighted


def schedule(conf, lb_ref):
    filters, cost_functions = _process_config(conf)
    devices = db_api.device_get_all(conf)
    if not devices:
        raise exp.DeviceNotFound
    filtered = _filter_devices(conf, lb_ref, devices, filters)
    weighted = _weight_devices(conf, lb_ref, filtered, cost_functions)
    return weighted[0][1]


def reschedule(conf, lb_ref):
    filters, cost_functions = _process_config(conf)
    device_ref = db_api.device_get(conf, lb_ref['device_id'])
    try:
        _filter_devices(conf, lb_ref, [device_ref], filters)
    except exp.NoValidDevice:
        devices = db_api.device_get_all(conf)
        devices = [dev_ref for dev_ref in devices
                       if dev_ref['id'] != device_ref['id']]
        filtered = _filter_devices(conf, lb_ref, devices, filters)
        weighted = _weight_devices(conf, lb_ref, filtered, cost_functions)
        return weighted[0][1]
    else:
        return device_ref


def filter_capabilities(conf, lb_ref, dev_ref):
    try:
        device_filter_capabilities = conf.device_filter_capabilities
    except cfg.NoSuchOptError:
        conf.register_opt(cfg.ListOpt('device_filter_capabilities',
                                      default=['algorithm']))
        device_filter_capabilities = conf.device_filter_capabilities
    device_driver = drivers.get_device_driver(conf, dev_ref['id'])
    capabilities = device_driver.get_capabilities()
    if capabilities is None:
        capabilities = {}
    for opt in device_filter_capabilities:
        lb_req = lb_ref.get(opt)
        if not lb_req:
            continue
        dev_caps = capabilities.get(opt + 's', [])
        if not (lb_req in dev_caps):
            LOG.debug('Device %s does not support %s "%s"', dev_ref['id'], opt,
                    lb_req)
            return False
    return True


def filter_vip(conf, lb_ref, dev_ref):
    vips = db_api.virtualserver_get_all_by_lb_id(conf, lb_ref['id'])
    if not vips:
        LOG.info('Loadbalancer %s has no VIPs, skipping VIP filter',
                 lb_ref['id'])
        return True
    if len(vips) > 1:
        LOG.error('VIP filter does not support more than one VIP per LB')
        return False
    vip = vips[0]['address']
    try:
        return dev_ref['extra']['sole_vip'] == vip
    except KeyError:
        return True


def lbs_on(conf, lb_ref, dev_ref):
    return db_api.lb_count_active_by_device(conf, dev_ref['id'])
