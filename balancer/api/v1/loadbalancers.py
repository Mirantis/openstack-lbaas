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

logger = logging.getLogger('balancer.api.v1.loadbalancers')


class Controller(object):

    def __init__(self, conf):
        logger.debug("Creating loadbalancers controller with config:"
                                                "loadbalancers.py %s", conf)
        self.conf = conf

    def findLBforVM(self, req, **args):
        logger.debug("Got index request. Request: %s", req)
        tenant_id = req.headers.get('X-Tenant-Id', "")
        params = {}
        params['vm_id'] = args['vm_id']
        params['tenant_id'] = tenant_id
        result = core_api.lb_find_for_vm(self.conf, **params)
        return {'loadbalancers': result}

    def index(self, req):
        logger.debug("Got index request. Request: %s", req)
        tenant_id = req.headers.get('X-Tenant-Id', "")
        result = core_api.lb_get_index(self.conf, tenant_id)
        return {'loadbalancers': result}

    @utils.http_success_code(202)
    def create(self, req, **args):
        logger.debug("Got create request. Request: %s", req)
        #here we need to decide which device should be used
        params = args['body']
        # We need to create LB object and return its id
        tenant_id = req.headers.get('X-Tenant-Id', "")
        lb_ref = db_api.loadbalancer_create(self.conf, {
                                                'tenant_id': tenant_id})
        params['lb'] = lb_ref
        core_api.create_lb(self.conf, **params)
        return {'loadbalancer': {'id': lb_ref['id']}}

    @utils.http_success_code(204)
    def delete(self, req, **args):
        logger.debug("Got delete request. Request: %s", req)
        core_api.delete_lb(self.conf, args['id'])

    def show(self, req, **args):
        logger.debug("Got loadbalancerr info request. Request: %s", req)
        result = core_api.lb_get_data(self.conf, args['id'])
        return {'loadbalancer': result}

    def showDetails(self, req, **args):
        logger.debug("Got loadbalancerr info request. Request: %s", req)
        result = core_api.lb_show_details(self.conf, args['id'])
        return result

    @utils.http_success_code(202)
    def update(self, req, **args):
        logger.debug("Got update request. Request: %s", req)
        core_api.update_lb(self.conf, args['id'], args['body'])
        return {'loadbalancers': "OK"}

    def addNodes(self, req, **args):
        logger.debug("Got addNode request. Request: %s", req)

        return core_api.lb_add_nodes(self.conf, args['id'],
                args['body']['nodes'])

    def showNodes(self, req, **args):
        logger.debug("Got showNodes request. Request: %s", req)
        return core_api.lb_show_nodes(self.conf, args['id'])

    def showNode(self, req, lb_id, lb_node_id):
        logger.debug("Got showNode request. Request: %s", req)
        return {'node': db_api.unpack_extra(
            db_api.server_get(self.conf, lb_node_id, lb_id))}

    @utils.http_success_code(204)
    def deleteNode(self, req, **args):
        logger.debug("Got deleteNode request. Request: %s", req)
        core_api.lb_delete_node(self.conf, args['id'],
                args['nodeID'])

    def changeNodeStatus(self, req, **args):
        logger.debug("Got changeNodeStatus request. Request: %s", req)
        result = core_api.lb_change_node_status(self.conf, args['id'],
                                                         args['nodeID'],
                                                         args['status'])
        return {"node": result}

    def updateNode(self, req, lb_id, lb_node_id, body):
        logger.debug("Got updateNode request. Request: %s", req)
        result = core_api.lb_update_node(self.conf, lb_id, lb_node_id, body)
        return {"node": result}

    def showMonitoring(self, req, **args):
        logger.debug("Got showMonitoring request. Request: %s", req)
        result = core_api.lb_show_probes(self.conf, args['id'])
        return result

    def showProbe(self, req, **args):
        logger.debug("Got showProbe request. Request: %s", req)
        probe = db_api.probe_get(self.conf, args['probeID'])
        return {"healthMonitoring": db_api.unpack_extra(probe)}

    def addProbe(self, req, lb_id, body):
        logger.debug("Got addProbe request. Request: %s", req)
        probe = core_api.lb_add_probe(self.conf, lb_id,
                                      body['healthMonitoring'])
        logger.debug("Return probe: %r", probe)
        return {'healthMonitoring': probe}

    @utils.http_success_code(204)
    def deleteProbe(self, req, **args):
        logger.debug("Got deleteProbe request. Request: %s", req)
        core_api.lb_delete_probe(self.conf, args['id'],
                args['probeID'])

    def showStickiness(self, req, **args):
        logger.debug("Got showStickiness request. Request: %s", req)
        result = core_api.lb_show_sticky(self.conf, args['id'])
        return result

    def showSticky(self, req, **args):
        logger.debug("Got showStickiness request. Request: %s", req)
        sticky = db_api.sticky_get(self.conf, args['stickyID'])
        return {"sessionPersistence": db_api.unpack_extra(sticky)}

    def addSticky(self, req, **args):
        logger.debug("Got addSticky request. Request: %s", req)
        sticky = core_api.lb_add_sticky(self.conf, args['id'],
                                       args['body'])
        return "{sessionPersistence:%s}" % sticky

    @utils.http_success_code(204)
    def deleteSticky(self, req, **args):
        logger.debug("Got deleteSticky request. Request: %s", req)
        core_api.lb_delete_sticky(self.conf, args['id'],
                args['stickyID'])

    def showVIPs(self, req, lb_id):
        logger.debug("Got showVIPs request. Request: %s", req)
        vips = map(db_api.unpack_extra,
                   db_api.virtualserver_get_all_by_lb_id(self.conf, lb_id))
        return {"vips": vips}


def create_resource(conf):
    """Loadbalancers resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
