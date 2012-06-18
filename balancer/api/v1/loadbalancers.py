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
import traceback

from openstack.common import exception
from openstack.common import wsgi

import webob

from balancer.api import v1 as api_v1
from balancer.api.v1 import filters
from balancer.core import api as core_api
from balancer.db import api as db_api

logger = logging.getLogger('balancer.api.v1.loadbalancers')


class Controller(object):

    def __init__(self, conf):
        logger.debug("Creating loadbalancers controller with config:"
                                                "loadbalancers.py %s", conf)
        self.conf = conf

    def findLBforVM(self, req, **args):
        try:
            logger.debug("Got index request. Request: %s", req)
            tenant_id = req.headers.get('X-Tenant-Id', "")
            tenant_name = req.headers.get('X-Tenant-Name', "")
            params = {}
            params['vm_id'] = args['vm_id']
            params['tenant_id'] = tenant_id
            params['tenant_name'] = tenant_name
            result = core_api.lb_find_for_vm(self.conf, **params)
            return {'loadbalancers': result}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def index(self, req):
        try:
            logger.debug("Got index request. Request: %s", req)
            tenant_id = req.headers.get('X-Tenant-Id', "")
            result = core_api.lb_get_index(self.conf, tenant_id)
            return {'loadbalancers': result}

        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'loadbalancers': list}

    def create(self, req, **args):
        try:
            logger.debug("Got create request. Request: %s", req)
            #here we need to decide which device should be used
            params = args['body']
            # We need to create LB object and return its id
            tenant_id = req.headers.get('X-Tenant-Id', "")
            lb_ref = db_api.loadbalancer_create(self.conf, {
                                                    'tenant_id': tenant_id})
            params['lb'] = lb_ref
            core_api.create_lb(self.conf, **params)
            return {'loadbalancers': {'id': lb_ref['id']}}
        except exception.NotFound:
            msg = "Exception occured "
            traceback.print_exc(file=sys.stdout)
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def delete(self, req, **args):
        try:
            logger.debug("Got delete request. Request: %s", req)
            core_api.delete_lb(self.conf, args['id'])
            return "OK"

        except exception.NotFound:
            msg = "Image with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def show(self, req, **args):
        try:
            logger.debug("Got loadbalancerr info request. Request: %s", req)
            result = core_api.lb_get_data(self.conf, args['id'])
            return {'loadbalancer': result}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showDetails(self, req, **args):
        try:
            logger.debug("Got loadbalancerr info request. Request: %s", req)
            result = core_api.lb_show_details(self.conf, args['id'])
            return result
        except exception.NotFound:
            msg = "Image with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def update(self, req, **args):
        try:
            logger.debug("Got update request. Request: %s", req)
            core_api.update_lb(self.conf, args['id'], args['body'])
            return {'loadbalancers': "OK"}
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def addNode(self, req, **args):
        try:
            logger.debug("Got addNode request. Request: %s", req)
            return core_api.lb_add_node(self.conf, args['id'],
                    args['body']['node'])
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showNodes(self, req, **args):
        try:
            logger.debug("Got showNodes request. Request: %s", req)
            return core_api.lb_show_nodes(self.conf, args['id'])
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def deleteNode(self, req, **args):
        try:
            logger.debug("Got deleteNode request. Request: %s", req)
            lb_node_id = core_api.lb_delete_node(self.conf, args['id'],
                                                            args['nodeID'])
            return "Deleted node with id %s" % lb_node_id
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def changeNodeStatus(self, req, **args):
        try:
            logger.debug("Got changeNodeStatus request. Request: %s", req)
            msg = core_api.lb_change_node_status(self.conf, args['id'],
                                                             args['nodeID'],
                                                             args['status'])
            return msg
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def updateNode(self, req, **args):
        try:
            logger.debug("Got updateNode request. Request: %s", req)
            msg = core_api.lb_update_node(self.conf, args['id'],
                                          args['nodeID'], args['body']['node'])
            return msg
        except exception.NotFound:
            msg = "LB with identifier %s or node with id %s not found" \
            % (args['id'], args['nodeID'])
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showMonitoring(self, req, **args):
        try:
            logger.debug("Got showMonitoring request. Request: %s", req)
            result = core_api.lb_show_probes(self.conf, args['id'])
            return result
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def addProbe(self, req, **args):
        try:
            logger.debug("Got addProbe request. Request: %s", req)
            probe_id = core_api.lb_add_probe(self.conf, args['id'],
                                   args['body']['healthMonitoring']['probe'])
            return "probe: %s" % probe_id
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def deleteProbe(self, req, **args):
        try:
            logger.debug("Got deleteProbe request. Request: %s", req)
            probe_id = core_api.lb_delete_probe(self.conf, args['id'],
                                                           args['probeID'])
            return "Deleted probe with id %s" % probe_id
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showStickiness(self, req, **args):
        try:
            logger.debug("Got showStickiness request. Request: %s", req)
            result = core_api.lb_show_sticky(self.conf, args['id'])
            return result
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def addSticky(self, req, **args):
        try:
            logger.debug("Got addSticky request. Request: %s", req)
            st_id = core_api.lb_add_sticky(self.conf, args['id'],
                                           args['body']['sessionPersistence'])
            return "sticky: %s" % st_id
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def deleteSticky(self, req, **args):
        try:
            logger.debug("Got deleteSticky request. Request: %s", req)
            sticky_id = core_api.lb_delete_sticky(self.conf, args['id'],
                                                             args['stickyID'])
            return "Deleted sticky with id %s" % sticky_id
        except exception.NotFound:
            msg = "LB with identifier %s not found" % args['id']
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def _get_query_params(self, req):
        """
        Extracts necessary query params from request.

        :param req: the WSGI Request object
        :retval dict of parameters that can be used by registry client
        """
        params = {'filters': self._get_filters(req)}

        for PARAM in api_v1.SUPPORTED_PARAMS:
            if PARAM in req.params:
                params[PARAM] = req.params.get(PARAM)
        return params

    def _get_filters(self, req):
        """
        Return a dictionary of query param filters from the request

        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        query_filters = {}
        for param in req.params:
            if param in api_v1.SUPPORTED_FILTERS or \
                    param.startswith('property-'):
                query_filters[param] = req.params.get(param)
                if not filters.validate(param, query_filters[param]):
                    raise webob.exc.HTTPBadRequest(
                            'Bad value passed to filter %s got %s' % (param,
                                                     query_filters[param]))
        return query_filters


def create_resource(conf):
    """Loadbalancers resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
