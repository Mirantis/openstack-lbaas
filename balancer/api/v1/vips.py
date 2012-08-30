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

from openstack.common import wsgi

from balancer.api import utils
from balancer.core import api as core_api
from balancer.db import api as db_api

LOG = logging.getLogger('balancer.api.v1.vips')


class Controller(object):
    def __init__(self, conf):
        LOG.debug("Creating virtualIps controller with config:"
                                                "vips.py %s", conf)
        self.conf = conf

    @utils.http_success_code(200)
    def index(self, req, lb_id):
        LOG.debug("Got index request. Request: %s", req)
        vips = map(db_api.unpack_extra,
                   db_api.virtualserver_get_all_by_lb_id(self.conf, lb_id))
        return {"virtualIps": vips}

    def create(self, req, lb_id, body):
        LOG.debug("Called create(), req: %r, lb_id: %s, body: %r",
                     req, lb_id, body)
        vip = core_api.lb_add_vip(self.conf, lb_id, body['virtualIp'])
        return {'virtualIp': vip}

    def show(self, req, lb_id, id):
        LOG.debug("Called show(), req: %r, lb_id: %s, id: %s",
                     req, lb_id, id)
        vip_ref = db_api.virtualserver_get(self.conf, id)
        return {'virtualIp': db_api.unpack_extra(vip_ref)}

    @utils.http_success_code(204)
    def delete(self, req, lb_id, id):
        LOG.debug("Called delete(), req: %r, lb_id: %s, id: %s",
                     req, lb_id, id)
        core_api.lb_delete_vip(self.conf, lb_id, id)


def create_resource(conf):
    """Virtual IPs resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
