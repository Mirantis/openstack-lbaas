# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import balancer.drivers.cisco_ace.ace_4x_driver
import balancer.drivers.cisco_ace.ace_5x_driver
import balancer.drivers.haproxy.HaproxyDriver


class DeviceMap(object):
    def __init__(self):
        self._map = {}

    def getDriver(self,  lbdevice):
        if lbdevice.type.lower() == "ace":
            if lbdevice.version.lower().startswith('a4'):
                return  balancer.drivers.cisco_ace.ace_4x_driver.AceDriver()
            else:
                return  balancer.drivers.cisco_ace.ace_5x_driver.AceDriver()
        if lbdevice.type.lower() == "haproxy":
            return balancer.drivers.haproxy.HaproxyDriver.HaproxyDriver()
        return None
