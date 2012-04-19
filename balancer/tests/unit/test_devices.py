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

from balancer.devices.device import LBDevice


class DeviceTestCase(unittest.TestCase):

    def test_device_defaults(self):
        device = LBDevice()
        device.name = "test"
        self.assertEquals(device.name,  "test")

    def test_device_load(self):
        device = LBDevice()
        params = {'name': "test",  'ip': '10.10.10.10'}
        device.loadFromDict(params)
        self.assertEqual(device.name,  "test")
