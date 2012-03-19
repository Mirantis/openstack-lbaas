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

class LBDevice(object):
    def __init__(self):
        self._name = None
        self._type = "ACE"
        self._version = None
        self._supports_IPv6 = False
        self._require_VIP_IP = True
        self._has_ACL = True
        self._supports_VLAN = True
    
    
    @property
    def Name(self):
        return self._name
    @Name.setter
    def Name(self,  value):
        self._name = value
    
    @property
    def Type(self):
        return self._type
    @Type.setter
    def Type(self,  value):
        self._type = value
    
    @property
    def Version(self):
        return self._version
    
    @Version.setter
    def Version(self,  value):
        self._version = value
    
    @property
    def Supports_IPv6(self):
        return self._supports_IPv6
    
    @property
    def Require_VIP_IP(self):
        return self._require_VIP_IP
    
    @property
    def Has_ACL(self):
        return self._has_ACL
    
    def Supports_VLAN(self):
        return self._supports_VLAN
        
