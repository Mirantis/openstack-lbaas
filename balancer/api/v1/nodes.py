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
        LOG.debug("Creating nodes controller with config:"
                                                "nodes.py %s", conf)
        self.conf = conf

    def create(self, req, lb_id, body):
        LOG.debug("Got addNode request. Request: %s", req)
        return {'nodes': core_api.lb_add_nodes(self.conf, lb_id,
            body['nodes'])}

    def index(self, req, lb_id):
        LOG.debug("Got showNodes request. Request: %s", req)
        return {'nodes': core_api.lb_show_nodes(self.conf, lb_id)}

    def show(self, req, lb_id, node_id):
        LOG.debug("Got showNode request. Request: %s", req)
        return {'node': db_api.unpack_extra(
            db_api.server_get(self.conf, node_id, lb_id))}

    @utils.http_success_code(204)
    def delete(self, req, lb_id, node_id):
        LOG.debug("Got deleteNode request. Request: %s", req)
        core_api.lb_delete_node(self.conf, lb_id, node_id)

    def changeNodeStatus(self, req, lb_id, node_id, status, body):
        LOG.debug("Got changeNodeStatus request. Request: %s", req)
        result = core_api.lb_change_node_status(self.conf, lb_id, node_id,
                                                         status)
        return {"node": result}

    def update(self, req, lb_id, node_id, body):
        LOG.debug("Got updateNode request. Request: %s", req)
        result = core_api.lb_update_node(self.conf, lb_id, node_id, body)
        return {"node": result}


def create_resource(conf):
    """Nodes resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
