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
import webob

from openstack.common import exception
from openstack.common import wsgi

from balancer.core.ServiceController import *
from balancer.core.LoadBalancerCommandsWorker import *
from balancer.core.Worker import *


from balancer.core.ServiceController import (ServiceController,  ServiceTask)

logger = logging.getLogger(__name__)

class Controller(object):

    def __init__(self, conf):
        msg = "Creating loadbalancers controller with config:loadbalancers.py %s" % conf
        logger.debug(msg)
        self.conf = conf
        self._service_controller = ServiceController.Instance()
        
        
    def index(self, req):
        try:
            msg = "Got index request. Request: %s" % req
            logger.debug(msg)
            
            list = self._servicecontroller.getTasks()
            return {'tasks' : list}

        except exception.NotFound:
            msg = "Image with identifier %s not found" % image_id
            logger.debug(msg)
            raise webob.exc.HTTPNotFound(msg)
        except exception.NotAuthorized:
            msg = _("Unauthorized image access")
            logger.debug(msg)
            raise webob.exc.HTTPForbidden(msg)
        return {}

def create_resource(conf):
    """Loadbalancers  resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
    


