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
from balancer.loadbalancers.loadbalancers import getLBRegistry
from balancer.core.ServiceController import *



logger = logging.getLogger('balancer.api.v1.loadbalancers')
SUPPORTED_PARAMS = balancer.api.v1.SUPPORTED_PARAMS
SUPPORTED_FILTERS = balancer.api.v1.SUPPORTED_FILTERS

class Controller(object):

    def __init__(self, conf):
        msg = "Creating loadbalancers controller with config: %s" % conf
        logger.debug(msg)
        self.conf = conf
        self._service_controller = ServiceController.Instance()
        pass
    
    def index(self, req):
        try:
            msg = "Got index request. Request: %s" % req
            logger.debug(msg)
            registry = getLBRegistry(self.conf)
            list = registry.getBlanacerList()
        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {'loadbalancers': list}
        
    def create(self,  req,  **args):
        msg = "Got create request. Request: %s Args: %s" % (req,  args)
        logger.debug(msg)
        registry = getLBRegistry()
        return {'status': "Done"}
        pass
        
    def loadbalancer_data(self,  req,  id):
        try:
            msg = "Got data request for balancer %s." % id
            logger.debug(msg)
            registry = loadbalancers.getLBRegistry()
            data  = registry.getBalancer(id)
        except exception.NotFound:
            msg = "Image with identifier %s not found"% image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = "Unauthorized image access"
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return dict(loadbalancer=data)
        
        
    def _get_query_params(self, req):
        """
        Extracts necessary query params from request.

        :param req: the WSGI Request object
        :retval dict of parameters that can be used by registry client
        """
        params = {'filters': self._get_filters(req)}

        for PARAM in SUPPORTED_PARAMS:
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
            if param in SUPPORTED_FILTERS or param.startswith('property-'):
                query_filters[param] = req.params.get(param)
                if not filters.validate(param, query_filters[param]):
                    raise HTTPBadRequest('Bad value passed to filter %s '
                                         'got %s' % (param,
                                                     query_filters[param]))
        return query_filters

def create_resource(conf):
    """Loadbalancers  resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
