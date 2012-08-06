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
import threading

from openstack.common import exception
#from balancer.storage.storage import *
from balancer.common.utils import Singleton
from balancer.db import api as db_api
from balancer import exception as exp

logger = logging.getLogger(__name__)


@Singleton
class Scheduller(object):

    def __init__(self, conf):
        self.conf = conf
        self._device_map = {}
        devices = db_api.device_get_all(conf)
        self._list = devices
        self._last_selected = 0
        self._device_count = 0
        self._lock = threading.RLock()
        for device in devices:
            self._device_map[device['id']] = device
            self._device_count += 1

    def getDevice(self):
        #TODO understand how we select device
        self._lock.acquire()
        try:
            logger.debug("Sehduller select device: current %s of %s",
                                self._last_selected, self._device_count)
            if self._last_selected >= (self._device_count - 1):
                self._last_selected = 0
                logger.debug("Sehduller select device: return %s",
                                self._last_selected)
                return self._list[self._last_selected]
            else:
                self._last_selected += 1
                logger.debug("Sehduller select device: return %s",
                                self._last_selected)
                return self._list[self._last_selected]
        finally:
            self._lock.release()

# NOTE(ash): broken, unused method
#    def getDeviceByLBid(self, id):
#        rd = self.store.getReader()
#        self._device_map = rd.getDeviceByLBid(id)
#        return self._device_map

    def getDeviceByID(self, id):
        if id == None:
            dev = self.getDevice()
        else:
            dev = self._device_map.get(id,  None)
            if dev == None:
                raise exception.NotFound(
                                "Can't find device specified by device ID.")
        return dev

    def getDevices(self):
        return self._list

    def addDevice(self, device):
        self._device_map[device['id']] = device
        self._list.append(device)
        self._device_count += 1


from balancer.common import cfg
import importlib

bind_opts = [
    cfg.ListOpt('device_filters', default=[]),
    cfg.ListOpt('device_cost_functions', default=[]),
]


def get_functions(opts):
    lst_functions = []
    if not opts:
        return []
    for opt in opts:
        func_name = opt.split('.')[-1]
        module_name = opt[:-len(func_name) - 1]
        module = importlib.import_module(module_name)
        lst_functions.append(module.__getattribute__(func_name))
    return lst_functions


def schedule_loadbalancer(conf, lb_ref):
    conf.register_opts(bind_opts)
    #get opts by conf.device_filters
    device_filters = get_functions(conf.device_filters)
    cost_functions = get_functions(conf.device_cost_functions)
    all_device = db_api.device_get_all(conf)
    for dev_func in device_filters:
        all_device = dev_func(all_device, lb_ref)
    for cost_func in cost_functions:
        all_device = cost_func(all_device)
    if not all_device:
        return None
    return all_device[0]
