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

from openstack.common import exception
from openstack.common import wsgi
from balancer import utils
from balancer.core import api as core_api
import balancer.db.api as db_api

LOG = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, conf):
        LOG.debug("Creating device controller with config: %s", conf)
        self.conf = conf

    @utils.require_admin
    def index(self, req):
        try:
            LOG.debug("Got index request. Request: %s", req)
            result = core_api.device_get_index(self.conf)
            LOG.debug("Obtained response: %s" % result)
            return {'devices': result}
        except exception.NotFound:
            msg = "Element not found"
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized access")
            LOG.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    @utils.require_admin
    def create(self, req, body):
        LOG.debug("Got create request. Request: %s", req)
        params = body
        LOG.debug("Request params: %s" % params)
        self._validate_params(params)
        device = core_api.device_create(self.conf, **params)
        return {"device": db_api.unpack_extra(device)}

    @utils.require_admin
    def show(self, req, device_id):
        LOG.debug("Got device data request. Request: %s" % req)
        device_ref = db_api.device_get(self.conf, device_id)
        return {'device': db_api.unpack_extra(device_ref)}

    def device_status(self, req, **args):
        # NOTE(yorik-sar): broken, there is no processing anymore
        try:
            shared = SharedObjects.Instance(self.conf)
            id = args['id']
            pool = shared.getDevicePoolbyID(id)
            stats = {}
            thr_stat = {}
            if pool:
                stats['command_queue_lenth'] = pool.getQueueSize()
                stats['threads'] = pool.getThreadCount()
                for i in range(pool.getThreadCount()):
                    thr_stat[i] = pool.get_status(i)
                stats['thread_status'] = thr_stat
                return {'device_command_status': stats}
            else:
                return {'device_command_status': 'not available'}
        except exception.NotFound:
            msg = "Device with id %s not found" % args['id']
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized access")
            LOG.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        finally:
            pass

    @utils.require_admin
    def info(self, req, **args):
        try:
            args['query_params'] = req.GET
            if worker.type == SYNCHRONOUS_WORKER:
                result = core_api.device_info(args)
                return {'devices': result}
        except exception.NotFound:
            msg = "Element not found"
            LOG.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized access")
            LOG.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'devices': list}

    @utils.http_success_code(204)
    @utils.require_admin
    def delete(self, req, device_id):
        LOG.debug("Got delete request. Request: %s", req)
        core_api.device_delete(self.conf, device_id)

    @utils.require_admin
    def show_algorithms(self, req):
        LOG.debug("Got algorithms request. Request: %s", req)
        algorithms = core_api.device_show_algorithms(self.conf)
        return {'algorithms': algorithms}

    @utils.require_admin
    def show_protocols(self, req):
        LOG.debug("Got protocols request. Request: %s", req)
        protocols = core_api.device_show_protocols(self.conf)
        return {'protocols': protocols}

    def _validate_params(self, params):
        pass


def create_resource(conf):
    """Devices  resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
