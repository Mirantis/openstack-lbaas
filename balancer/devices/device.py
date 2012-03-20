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
        self._id = None
        self._name = None
        self._type = "ACE"
        self._version = None
        self._supports_IPv6 = False
        self._require_VIP_IP = True
        self._has_ACL = True
        self._supports_VLAN = True
    
    def loadFromRow(self,  row):
        self._id = row[0]
        self._name = row[1]
        self._type = row[2]
        self._version = row[3]
        self._supports_IPv6 = row[4]
        self._require_VIP_IP = row[5]
        self._has_ACL = row[6]
        self._supports_VLAN = row[7]
    
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self,  value):
        self._id = value
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,  value):
        self._name = value
    
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self,  value):
        self._type = value
    
    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self,  value):
        self._version = value
    
    @property
    def supports_IPv6(self):
        return self._supports_IPv6
        
    @supports_IPv6.setter
    def supports_IPv6(self,  value):
        self._supports_IPv6 = value
    
    
    @property
    def require_VIP_IP(self):
        return self._require_VIP_IP
        
    @require_VIP_IP.setter
    def require_VIP_IP(self,  value):
        self._require_VIP_IP = value


    @property
    def has_ACL(self):
        return self._has_ACL
    @has_ACL.setter
    def has_ACL(self,  value):
        self._has_ACL = value

    @property
    def supports_VLAN(self):
        return self._supports_VLAN
        
    @supports_VLAN.setter
    def supports_VLAN(self,  value):
        self._supports_VLAN  = value
