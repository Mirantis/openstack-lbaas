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
import sys
import  balancer.loadbalancers

from openstack.common import exception
from openstack.common import wsgi
from balancer.devices.device import LBDevice

from balancer.core.ServiceController import *
from balancer.core.deviceworkers import *
from balancer.core.Worker import *
from balancer.processing.sharedobjects import SharedObjects

logger = logging.getLogger('balancer.api.v1.devices')


class Controller(object):

    def __init__(self, conf):
        msg = "Creating device controller with config: %s" % conf
        logger.debug(msg)
        self.conf = conf
        self._service_controller = ServiceController.Instance()
        pass

    def index(self,  req):
        try:
            msg = "Got index request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = DeviceActionMapper()
            worker = mapper.getWorker(task, "index")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                logger.debug("Obtained response: %s" % result)
                return {'devices': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'task_id': task.id}

        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

        pass

    def create(self, req, **args):
        msg = "Got create request. Request: %s" % req
        logger.debug(msg)
        try:
            params = args['body']
            msg = "Request params: %s" % params
            logger.debug(msg)
            self._validate_params(params)
            task = self._service_controller.createTask()
            task.parameters = params
            mapper = DeviceActionMapper()
            worker = mapper.getWorker(task, "create")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()

                return {'devices': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'task_id': task.id}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'devices': list}

    def show(self, req, **args):
        msg = "Got device data request. Request: %s Arguments: %s" \
        % (req, args)
        logger.debug(msg)
        try:

            return {"list": "OK"}
            logger.debug(msg)
            self._validate_params(params)
            task = self._service_controller.createTask()
            task.parameters = params
            mapper = DeviceActionMapper()
            worker = mapper.getWorker(task, "show")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()

                return {'devices': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'task_id': task.id}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'devices': list}
        
    def device_status(self, req,  **args):
        try:
            shared = SharedObjects.Instance()
            id = args['id']
            pool = shared.getDevicePoolbyID(id)
            stats = {}
            thr_stat={}
            if pool:
                stats['command_queue_lenth'] = pool.getQueueSize()
                stats['threads'] = pool.getThreadCount()
                for i in range(pool.getThreadCount()):
                    thr_stat[i] = pool.get_status(i)
                stats['thread_status'] = thr_stat
                return {'device_command_status' : stats}
            else:
                return {'device_command_status' : 'not available'}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        finally:
            pass

    def device_info(self, req, **args):
        try:

            task = self._service_controller.createTask()
            task.parameters = args
            task.parameters['query_params'] = req.GET
            mapper = DeviceActionMapper()
            worker = mapper.getWorker(task, "info")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()

                return {'devices': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'task_id': task.id}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'devices': list}

    def _validate_params(self,  params):
        pass


def create_resource(conf):
    """Devices  resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
