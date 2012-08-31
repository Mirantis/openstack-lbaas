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

        tenant_mapper = mapper.submapper(path_prefix="/{tenant_id}")

        lb_resource = loadbalancers.create_resource(self.conf)
        lb_collection = tenant_mapper.collection(
                "loadbalancers", "loadbalancer",
                controller=lb_resource, member_prefix="/{lb_id}",
                formatted=False)
        lb_collection.member.link('details')

        lb_collection.connect("/find_for_VM/{vm_id}",
                       action="findLBforVM", conditions={'method': ["GET"]})

        nd_resource = nodes.create_resource(self.conf)
        nd_collection = lb_collection.member.collection('nodes', 'node',
                controller=nd_resource, member_prefix="/{node_id}",
                formatted=False)
        nd_collection.member.connect("/{status}", action="changeNodeStatus",
                   conditions={'method': ["PUT"]})

        pb_resource = probes.create_resource(self.conf)

        lb_collection.member.collection('healthMonitoring', '',
                controller=pb_resource, member_prefix="/{probe_id}",
                formatted=False)

        st_resource = stickies.create_resource(self.conf)

        lb_collection.member.collection('sessionPersistence', '',
                controller=st_resource, member_prefix="/{sticky_id}",
                formatted=False)

        vip_resource = vips.create_resource(self.conf)

        lb_collection.member.collection('virtualIps', 'virtualIp',
                controller=vip_resource, member_prefix="/{vip_id}",
                formatted=False)

        device_resource = devices.create_resource(self.conf)

        device_collection = mapper.collection('devices', 'device',
                controller=device_resource, member_prefix="/{device_id}",
                formatted=False)
        device_collection.member.link('info')

        # NOTE(yorik-sar): broken
        #mapper.connect("/devices/{id}/status", controller=device_resource,
        #               action="device_status")

        mapper.connect("/algorithms",
                       controller=device_resource,
                       action="show_algorithms",
                       conditions={'method': ["GET"]})
        mapper.connect("/protocols",
                       controller=device_resource,
                       action="show_protocols",
                       conditions={'method': ["GET"]})

        super(API, self).__init__(mapper)
