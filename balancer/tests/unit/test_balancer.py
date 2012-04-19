# Copyright 2012 OpenStack LLC.
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

import os
import sys
import unittest

from balancer.loadbalancers.vserver import Balancer
from openstack.common.wsgi import JSONRequestDeserializer


class BalancerTestCase(unittest.TestCase):
    class RequestMock(object):
        def __init__(self,  body):
            self.body = body
            self.content_length = len(body)
            self.headers = {'Content length': self.content_length,  \
                           'transfer-encoding': 'chunked',  \
                           'Content-Type': 'application/json'}

    def test_balancer_parse(self):
        bl = Balancer()
        file = open("./balancer/tests/unit/createLBcommand")
        body = file.read()
        file.close()
        req = BalancerTestCase.RequestMock(body)
        serializer = JSONRequestDeserializer()
        parsed = serializer.default(req)
        params = parsed['body']

        bl.parseParams(params)

        if bl.sf.lb_id != bl.lb.id:
            self.fail("SF.lb_id does not point ot LB id")

        for rs in bl.rs:
            if rs.sf_id != bl.sf.id:
                self.fail("RS.sf_id does not point to SF id")

        for vip in bl.vips:
            if vip.sf_id != bl.sf.id:
                self.fail("VIp.sf_id does not point to SF id")
            if vip.lb_id != bl.lb.id:
                self.fail("Vip.lb_id does not point to LB id")
