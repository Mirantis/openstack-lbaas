# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
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

import balancer.loadbalancers.loadbalancer
from balancer.storage.storage import *
from balancer.common.utils import Singleton


class LBCache(object):
    class LBCacheEntry:
        def __init__(self, lb):
            self._lb = lb
            self._dirty = False

        @property
        def entry(self):
            return self._lb

        @property
        def dirty(self):
            return self._dirty

        def mark(self):
            self._drity = True

    def __init__(self):
        self._entries = {}

    def addEntry(self,  lb):
        self._entries[lb.id] = LBCacheEntry(lb)

    def getEntry(self,  id):
        entry = self._entries.get(k,  None)
        if entry != None:
            return entry.entry
        else:
            return None

    def removeEntry(self,  id):
        #TODO check for existance
        del self._entries[id]


@Singleton
class LoadbalancerRegistry(object):

    def __init__(self):
        self._init = False
        pass

    def init(self,  conf):
        if not self._init:
            self._storage = Storage(conf)
            self._cache = LBCache()
            self._init = True

    def addBalancer(self, lb_balancer):
        #TODO add some logic here to return data from cache
        wr = self._storage.getWriter()
        wr.writeLoadBalancer(lb_balancer)
        self._cache.addEntry(lb_balancer)
        pass

    def getBalancer(self,  id):
        #TODO Add exception handling here
        lb = self._cache.getEntry(id)
        if lb != None:
            return lb
        else:
            reader = self._storage.getReader()
            lb = reader.getLoadBalancerById(id)
            self._cache.addEntry(lb)
            return lb

    def getBlanacerList(self):
        reader = self._storage.getReader()
        lb_list = reader.getLoadBalancers()
        for lb in lb_list:
            self._cache.addEntry(lb)
        return lb_list


def getLBRegistry(conf):
    lbr = LoadbalancerRegistry.Instance(conf)
    lbr.init(conf)
    return lbr
