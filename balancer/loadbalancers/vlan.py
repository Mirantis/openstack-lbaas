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

import logging

from balancer.core.serializeable import Serializeable
from balancer.core.uniqueobject import UniqueObject


class VLAN(Serializeable,  UniqueObject):
    def __init__(self):
        
        Serializeable.__init__(self)
        UniqueObject.__init__(self)
        
        self.description = ""
        self.intType = "Routed"
        self.IPaddr = ""
        self.aliasIPaddr = ""
        self.peerIPaddr = ""
        self.netmask = ""
        self.adminStatus = "Up"
        self.enableMACsticky = None
        self.enableNormalization = "IPv4v6"
        self.enableIPv6 = None
        self.ipv6GlobalIP = [] #possible use as ["IPv6Address","eui-64","aliasIPv6Address","peerIPv6Address","eui-64","prefixLength"]
        #                                                          ["2002:1:2:3::1","0","2002:2:3:4::1","2002:3:4:5::1","0","80"]
        self.ipv6UniqueLocalAddr = [] #possible use as ["IPv6Address","eui-64","peerIPv6Address","eui-64","prefixLenght"]
        #                                                                        ["fb8:22:22::1","0","fb8:23:23::1","0","64"]
        self.ipv6LinkLocalAddr = ""
        self.ipv6PeerLinkLocalAddr = ""
        self.enableICMPguard = "IPv4v6"
        self.enableDHCPrelay = ""# "Ipv4v6" or "IPv4" or "IPv6"
        self.RPF = ""
        self.reassemblyTimeout = ["5", "60"] # ["ipv4","ipv6"]
        self.maxFragChainsAllowed = ["24", "24"] 
        self.minFragMTUvalue = ["576", "1280"]
        self.MTU = ["1500", "1500"]
        self.actionForIPheaderOptions = ["Clear-Invalid", "Drop"]
        self.enableMACAddrAutogen = None
        self.minTTLipHeaderValue = ""
        self.enableSynCookieThreshValue = ""
        self.actionForDBfit = "Allow"
        self.ARPinspectType = None
        self.UDPconfigCommands = None
        self.secondaryIPgroups = [] # ["IP","aliasIP","peerIP","netmask"]
        self.inputPolicies = []
        self.inputAccessGroup = []
        self.outputAccessGroup = []
