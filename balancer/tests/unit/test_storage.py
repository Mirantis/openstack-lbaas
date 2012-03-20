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
from openstack.common import exception
from balancer.devices.device import LBDevice
class StorageTestCase(unittest.TestCase):
    
    def test_device_save(self):
        device = LBDevice()
        device.id = 111
        device.name = "DeviceName001"
        device.type = "ACE"
        device.version = "1.0"
        device.require_VIP_IP = True
        device.has_ACL = True
        device.supports_VLAN = False
        stor = Storage( {'db_path':'./db/testdb.db'})
        wr = stor.getWriter()
        wr.writeDevice(device)
        read  = stor.getReader()
        new_device = read.getDeviceById(111)
        self.assertEquals(new_device.name,  "DeviceName001")
        
    
    def test_lb_save(self):
        lb = LoadBalancer()
        lb.name  = "testLB"
        lb.id = 123
        lb.algorithm = "ROUND_ROBIN"
        lb.staus = "ACTIVE"
        lb.created = "01-01-2012 11:22:33"
        lb.updated = "02-02-2012 11:22:33"
        stor = Storage( {'db_path':'./db/testdb.db'})
        wr = stor.getWriter()
        wr.writeLoadBalancer(lb)
        read  = stor.getReader()
        newlb = read.getLoadBalancerById(123)
        self.assertEquals(newlb.name,  "testLB")
    
    def test_exception_on_nonexistent_lb(self):
        stor = Storage( {'db_path':'./db/testdb.db'})
        read  = stor.getReader()
        try:
            newlb = read.getLoadBalancerById(1234)
        except exception.NotFound:
            pass
        else:
            self.fail("No exception was raised for non-existent LB")
            
    def test_multiple_lb_select(self):
        lb = LoadBalancer()
        lb.name  = "testLB2"
        lb.id = 124
        lb.algorithm = "ROUND_ROBIN"
        lb.staus = "ACTIVE"
        lb.created = "01-01-2012 11:22:33"
        lb.updated = "02-02-2012 11:22:33"
        stor = Storage( {'db_path':'./db/testdb.db'})
        wr = stor.getWriter()
        wr.writeLoadBalancer(lb)
        lb.name  = "testLB3"
        lb.id = 125
        lb.algorithm = "ROUND_ROBIN"
        lb.staus = "DOWN"
        lb.created = "01-01-2012 11:22:33"
        lb.updated = "02-02-2012 11:22:33"
        wr.writeLoadBalancer(lb)
        read  = stor.getReader()
        lb_list = read.getLoadBalancers()
        self.assertEquals(len(lb_list), 3)
    
    
    
