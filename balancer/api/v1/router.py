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

import routes

from . import loadbalancers
from . import devices
from . import nodes
from . import vips
from . import probes
from . import stickies
#from . import tasks


from openstack.common import wsgi


logger = logging.getLogger(__name__)


class API(wsgi.Router):

    """WSGI router for balancer v1 API requests."""

    def __init__(self, conf, **local_conf):
        self.conf = conf
        mapper = routes.Mapper()

        lb_resource = loadbalancers.create_resource(self.conf)
        nd_resource = nodes.create_resource(self.conf)

        mapper.resource("loadbalancer", "loadbalancers", \
         member={'details': 'GET'}, \
         controller=lb_resource, collection={'detail': 'GET'})

        mapper.resource('node', 'nodes', controller=nd_resource,\
         parent_resource={'member_name': 'lb',\
         'collection_name': 'loadbalancers'})

        mapper.connect("/loadbalancers/find_for_VM/{vm_id}",
                       controller=lb_resource,
                       action="findLBforVM", conditions={'method': ["GET"]})

        mapper.connect("/loadbalancers/{lb_id}/nodes/{id}/{status}", \
                       controller=nd_resource, action="changeNodeStatus", \
                       conditions={'method': ["PUT"]})

        pb_resource = probes.create_resource(self.conf)

        mapper.resource('', 'healthMonitoring', \
         controller=pb_resource, \
         parent_resource={'member_name': 'lb',\
         'collection_name': 'loadbalancers'})

        st_resource = stickies.create_resource(self.conf)

        mapper.resource('', 'sessionPersistence', \
         controller=st_resource, \
         parent_resource={'member_name': 'lb',\
         'collection_name': 'loadbalancers'})

        vip_resource = vips.create_resource(self.conf)

        mapper.resource("virtualIp", "virtualIps",\
         controller=vip_resource,\
         parent_resource={'member_name': 'lb',\
         'collection_name': 'loadbalancers'})

        device_resource = devices.create_resource(self.conf)

        mapper.resource("device", "devices", controller=device_resource,
                        collection={'detail': 'GET'})

        mapper.connect("/devices/", controller=device_resource,
                action="index")

        mapper.connect("/devices/{id}", controller=device_resource,
                       action="show")
#                       conditions=dict(method=["GET"]))
        # NOTE(yorik-sar): broken
        #mapper.connect("/devices/{id}/status", controller=device_resource,
        #               action="device_status")
        mapper.connect("/devices/{id}/info",
                controller=device_resource,
                       action="device_info")

        mapper.connect("/devices/",
                       controller=device_resource,
                       action="create",
                       conditions={'method': ["POST"]})

        mapper.connect("/algorithms",
                       controller=device_resource,
                       action="show_algorithms",
                       conditions={'method': ["GET"]})
        mapper.connect("/protocols",
                       controller=device_resource,
                       action="show_protocols",
                       conditions={'method': ["GET"]})
       # TODO(yorik-sar): tasks are broken, there is no processing anymore
        #tasks_resource = tasks.create_resource(self.conf)
        #mapper.resource("tasks", "tasks", controller=tasks_resource,
        #                collection={'detail': 'GET'})
        #mapper.connect("/service/processing", controller=tasks_resource,
        #               action="index_processing")

        super(API, self).__init__(mapper)
