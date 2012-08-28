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
        LOG.debug("Creating sessionPersistence controller with config:"
                                                "stickies.py %s", conf)
        self.conf = conf

    @utils.http_success_code(204)

    def showStickiness(self, req, lb_id):
        LOG.debug("Got showStickiness request. Request: %s", req)
        result = core_api.lb_show_sticky(self.conf, id)
        return result

    def showSticky(self, req, lb_id, id):
        LOG.debug("Got showStickiness request. Request: %s", req)
        sticky = db_api.sticky_get(self.conf, id)
        return {"sessionPersistence": db_api.unpack_extra(sticky)}

    def addSticky(self, req, lb_id, body):
        LOG.debug("Got addSticky request. Request: %s", req)
        sticky = core_api.lb_add_sticky(self.conf, id, body)
        return {"sessionPersistence": db_api.unpack_extra(sticky)}

    @utils.http_success_code(204)
    def deleteSticky(self, req, lb_id, id):
        LOG.debug("Got deleteSticky request. Request: %s", req)
        core_api.lb_delete_sticky(self.conf, lb_id, id)

def create_resource(conf):
    """Session persistence resource factory method"""
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(conf), deserializer, serializer)
