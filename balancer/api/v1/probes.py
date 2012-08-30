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

LOG = logging.getLogger(__name__)


class Controller(object):

    def __init__(self, conf):
        LOG.debug("Creating probes controller with config:"
                                                "probes.py %s", conf)
        self.conf = conf

    @utils.http_success_code(204)
    def index(self, req, lb_id):
        LOG.debug("Got showMonitoring request. Request: %s", req)
        result = core_api.lb_show_probes(self.conf, lb_id)
        return result

    def show(self, req, lb_id, id):
        LOG.debug("Got showProbe request. Request: %s", req)
        probe = db_api.probe_get(self.conf, id)
        return {"healthMonitoring": db_api.unpack_extra(probe)}

    def create(self, req, lb_id, body):
        LOG.debug("Got addProbe request. Request: %s", req)
        probe = core_api.lb_add_probe(self.conf, lb_id,
                                      body['healthMonitoring'])
        LOG.debug("Return probe: %r", probe)
        return {'healthMonitoring': probe}

    @utils.http_success_code(204)
    def delete(self, req, lb_id, id):
        LOG.debug("Got deleteProbe request. Request: %s", req)
        core_api.lb_delete_probe(self.conf, lb_id, id)


def create_resource(conf):
    """Health monitoring resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
