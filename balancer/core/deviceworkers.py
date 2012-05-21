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

from balancer.core.Worker import *
from balancer.storage.storage import *
from balancer.core.ServiceController import *

logger = logging.getLogger(__name__)


class DeviceGetIndexWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(DeviceGetIndexWorker,  self).__init__(task, conf)

    def run(self):
        self._task.status = STATUS_PROGRESS
        store = Storage(self._conf)
        reader = store.getReader()
        list = reader.getDevices()
        self._task.status = STATUS_DONE
        return list


class DeviceCreateWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(DeviceCreateWorker, self).__init__(task, conf)

    def run(self):
        self._task.status = STATUS_PROGRESS
        params = self._task.parameters
        dev = LBDevice()
        dev.loadFromDict(params)

        store = Storage(self._conf)
        writer = store.getWriter()
        writer.writeDevice(dev)
        sc = ServiceController.Instance(self._conf)
        sched = sc.scheduler
        sched.addDevice(dev)
        self._task.status = STATUS_DONE
        return 'OK'


class DeviceInfoWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(DeviceInfoWorker, self).__init__(task, conf)

    def run(self):
        self._task.status = STATUS_PROGRESS
        params = self._task.parameters
        query = params['query_params']
        msg = "DeviceInfoWorker start with Params: %s Query: %s" \
            % (params,  query)
        logger.debug(msg)
        self._task.status = STATUS_DONE
        return 'OK'


class DeviceDeleteWorker(SyncronousWorker):
    def __init__(self,  task, conf):
        super(DeviceDeleteWorker, self).__init__(task, conf)

    def run(self):
        self._task.status = STATUS_PROGRESS
        params = self._task.parameters
        dev = LBDevice()
        dev.loadFromDict(params)

        store = Storage(self._conf)
        writer = store.getWriter()
        writer.writeDevice(dev)
        sc = ServiceController.Instance(self._conf)
        sched = sc.scheduler
        sched.addDevice(dev)
        self._task.status = STATUS_DONE
        return 'OK'


class DeviceActionMapper(object):
    def getWorker(self, task,  action, conf,  params=None):
        if action == "index":
            return DeviceGetIndexWorker(task, conf)
        if action == "create":
            return DeviceCreateWorker(task, conf)
        if action == "info":
            return DeviceInfoWorker(task, conf)
        if action == "delete":
            return DeviceDeleteWorker(task, conf)
