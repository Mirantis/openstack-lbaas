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

import  balancer.loadbalancers.loadbalancer

from openstack.common import exception
from openstack.common import wsgi

from balancer.core.ServiceController import *
from balancer.core.LoadBalancerCommandsWorker import *
from balancer.core.Worker import *


logger = logging.getLogger('balancer.api.v1.loadbalancers')
SUPPORTED_PARAMS = balancer.api.v1.SUPPORTED_PARAMS
SUPPORTED_FILTERS = balancer.api.v1.SUPPORTED_FILTERS

class Controller(object):

    def __init__(self, conf):
        msg = "Creating loadbalancers controller with config:loadbalancers.py %s" % conf
        logger.debug(msg)
        self.conf = conf
        self._service_controller = ServiceController.Instance()
        pass
    
    def index(self, req):
        try:
            msg = "Got index request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()
            worker = mapper.getWorker(task, "index" )
            if worker.type ==  SYNCHRONOUS_WORKER:
                result = worker.run()
                return {'loadbalancers': result}
            
            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers' : task.id}

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
        try:
            msg = "Got create request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper =LBActionMapper()
            #here we need to decide which device should be used
            params = args['body']
            # We need to create LB object and return its id
            lb = balancer.loadbalancers.loadbalancer.LoadBalancer()
            params['lb'] = lb
            task.parameters = params
            worker = mapper.getWorker(task, "create" )
            if worker.type ==  SYNCHRONOUS_WORKER:
                result = worker.run()
                return {'loadbalancers': {"id": lb.id}}
            
            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers' : {'id':lb.id}}

        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

        
    def loadbalancer_data(self,  req,  id):
       pass
        
        
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
