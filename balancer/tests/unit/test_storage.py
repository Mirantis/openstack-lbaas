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


from balancer.storage.storage import *
from balancer.loadbalancers.loadbalancer import LoadBalancer

class StorageTestCase(unittest.TestCase):
    
    def test_lb_save(self):
        lb = LoadBalancer()
        lb.name  = "testLB"
        lb.id = 123
        lb.algorithm = "ROUND_ROBIN"
        lb.staus = "ACTIVE"
        lb.created = "01-01-2012 11:22:33"
        lb.updated = "02-02-2012 11:22:33"
        stor = Storage('/home/gokrokve/work/OpenStack/balancer/db/balancer.db')
        wr = stor.getWriter()
        wr.writeLoadBalancer(lb)
        read  = stor.getReader()
        newlb = read.getLoadBalancerById(123)
        self.assertEquals(newlb.name,  "testLB")
    
    
