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

import  balancer.loadbalancers.loadbalancer

from openstack.common import exception
from openstack.common import wsgi

from balancer.core.ServiceController import *
from balancer.core.LoadBalancerCommandsWorker import *
from balancer.core.Worker import *
import webob

logger = logging.getLogger('balancer.api.v1.loadbalancers')
SUPPORTED_PARAMS = balancer.api.v1.SUPPORTED_PARAMS
SUPPORTED_FILTERS = balancer.api.v1.SUPPORTED_FILTERS


class Controller(object):

    def __init__(self, conf):
        msg = "Creating loadbalancers controller with config:loadbalancers.py \
        %s" % conf
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
            worker = mapper.getWorker(task, "index")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return {'loadbalancers': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': task.id}

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
            msg = "Got create request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()
            #here we need to decide which device should be used
            params = args['body']
            # We need to create LB object and return its id
            lb = balancer.loadbalancers.loadbalancer.LoadBalancer()
            params['lb'] = lb
            task.parameters = params
            worker = mapper.getWorker(task, "create")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return {'loadbalancers': {"id": lb.id}}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': {'id': lb.id}}

        except exception.NotFound :
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
            msg = "Got delete request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()
            #here we need to decide which device should be used
            #params = args['body']
            params = args['id']
            task.parameters = params
            worker = mapper.getWorker(task, "delete")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return "OK"

        except exception.NotFound:
            msg = "Image with identifier %s not found" % params
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def show(self, req, **args):
        try:
            msg = "Got loadbalancerr info request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()
            #here we need to decide which device should be used
            #params = args['body']
            params = args
            task.parameters = params
            worker = mapper.getWorker(task, "show")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return{'loadbalancer': result}

        except exception.NotFound:
            msg = "Image with identifier %s not found" % params
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showDetails(self, req, **args):
        try:
            msg = "Got loadbalancerr info request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()
            #here we need to decide which device should be used
            #params = args['body']
            params = args
            task.parameters = params
            worker = mapper.getWorker(task, "showDetails")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

        except exception.NotFound:
            msg = "Image with identifier %s not found" % params
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def update(self, req, **args):
        try:
            msg = "Got update request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            #here we need to decide which device should be used
            params = {}
            params['body'] = args['body']
            params['id'] = args['id']
            task.parameters = params

            worker = mapper.getWorker(task, "update")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return {'loadbalancers': result}

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
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
            msg = "Got addNode request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            #here we need to decide which device should be used
            params = {}
            body = args['body']
            params['node'] = body['node']
            params['id'] = args['id']
            task.parameters = params

            worker = mapper.getWorker(task, "addNode")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got showNodes request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            #here we need to decide which device should be used
            params = {}
            params['id'] = args['id']
            task.parameters = params

            worker = mapper.getWorker(task, "showNodes")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got deleteNode request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            params['nodeID'] = args['nodeID']
            task.parameters = params

            worker = mapper.getWorker(task, "deleteNode")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got changeNodeStatus request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            params['nodeID'] = args['nodeID']
            params['status'] = args['status']
            task.parameters = params

            worker = mapper.getWorker(task, "changeNodeStatus")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got updateNode request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            params['nodeID'] = args['nodeID']
            body = args['body']
            params['node'] = body['node']
            task.parameters = params

            worker = mapper.getWorker(task, "updateNode")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

        except exception.NotFound:
            msg = "LB with identifier %s or node with id %s not found" \
            % (args['id'],  args['nodeID'])
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = ("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)

    def showMonitoring(self, req, **args):
        try:
            msg = "Got showMonitoring request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            task.parameters = params

            worker = mapper.getWorker(task, "showProbes")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got addProbe request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            body = args['body']
            params['probe'] = body['healthMonitoring']
            task.parameters = params

            worker = mapper.getWorker(task, "LBAddProbe")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got deleteProbe request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            params['probeID'] = args['probeID']
            task.parameters = params

            worker = mapper.getWorker(task, "LBdeleteProbe")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got showStickiness request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            task.parameters = params

            worker = mapper.getWorker(task, "showSticky")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got addSticky request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            body = args['body']
            params['sticky'] = body['sessionPersistence']
            task.parameters = params

            worker = mapper.getWorker(task, "addSticky")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
            msg = "Got deleteSticky request. Request: %s" % req
            logger.debug(msg)
            task = self._service_controller.createTask()
            mapper = LBActionMapper()

            params = {}
            params['id'] = args['id']
            params['stickyID'] = args['stickyID']
            task.parameters = params

            worker = mapper.getWorker(task, "deleteSticky")
            if worker.type == SYNCHRONOUS_WORKER:
                result = worker.run()
                return result

            if worker.type == ASYNCHRONOUS_WORKER:
                task.worker = worker
                self._service_controller.addTask(task)
                return {'loadbalancers': "OK"}

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
