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

class VLAN(object):
    def __init__(self):
        self._id = None
        self._description = ""
        self._intType = "Routed"
        self._IPaddr = ""
        self._aliasIPaddr = ""
        self._peerIPaddr = ""
        self._netmask = ""
        self._adminStatus = "Up"
        self._enableMACsticky = None
        self._enableNormalization = "IPv4v6"
        self._enableIPv6 = None
        self._ipv6GlobalIP = [] #possible use as ["IPv6Address","eui-64","aliasIPv6Address","peerIPv6Address","eui-64","prefixLength"]
        #                                                          ["2002:1:2:3::1","0","2002:2:3:4::1","2002:3:4:5::1","0","80"]
        self._ipv6UniqueLocalAddr = [] #possible use as ["IPv6Address","eui-64","peerIPv6Address","eui-64","prefixLenght"]
        #                                                                        ["fb8:22:22::1","0","fb8:23:23::1","0","64"]
        self._ipv6LinkLocalAddr = ""
        self._ipv6PeerLinkLocalAddr = ""
        self._enableICMPguard = "IPv4v6"
        self._enableDHCPrelay = ""# "Ipv4v6" or "IPv4" or "IPv6"
        self._RPF = ""
        self._reassemblyTimeout = ["5", "60"] # ["ipv4","ipv6"]
        self._maxFragChainsAllowed = ["24", "24"] 
        self._minFragMTUvalue = ["576", "1280"]
        self._MTU = ["1500", "1500"]
        self._actionForIPheaderOptions = ["Clear-Invalid", "Drop"]
        self._enableMACAddrAutogen = None
        self._minTTLipHeaderValue = ""
        self._enableSynCookieThreshValue = ""
        self._actionForDBfit = "Allow"
        self._ARPinspectType = None
        self._UDPconfigCommands = None
        self._secondaryIPgroups = [] # ["IP","aliasIP","peerIP","netmask"]
        self._inputPolicies = []
        self._inputAccessGroup = []
        self._outputAccessGroup = []

    def loadFromRow(self,  row):
        #TODO implement this
        msg = 'LoadBalancer create from row. Id: %s' % row[0]
        logger.debug(msg)
        self._id = row[0]
        self._description = row[1]
        self._intType = row[2]
        self._IPaddr = row[3]
        self._aliasIPaddr = row[4]
        self._peerIPaddr = row[5]
        self._netmask = row[6]
        self._adminStatus = row[7]
        self._enableMACsticky = row[8]
        self._enableNormalization = row[9]
        self._enableIPv6 = row[10]
        self._ipv6GlobalIP = row[11]
        self._ipv6UniqueLocalAddr = row[12]
        self._ipv6LinkLocalAddr = row[13]
        self._ipv6PeerLinkLocalAddr = row[14]
        self._enableICMPguard = row[15]
        self._enableDHCPrelay = row[16]
        self._RPF = row[17]
        self._reassemblyTimeout = row[18]
        self._maxFragChainsAllowed = row[19]
        self._minFragMTUvalue = row[20]
        self._MTU = row[21]
        self._actionForIPheaderOptions = row[22]
        self._enableMACAddrAutogen = row[23]
        self._minTTLipHeaderValue = row[24]
        self._enableSynCookieThreshValue = row[25]
        self._actionForDBfit = row[26]
        self._ARPinspectType = row[27]
        self._UDPconfigCommands = row[28]
        self._secondaryIPgroups = row[29]
        self._inputPolicies = row[30]
        self._inputAccessGroup = row[31]
        self._outputAccessGroup = row[32]
        

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, value):
        self._description = value
    @property
    def intType(self):
        return self._intType
    @intType.setter
    def intType(self, value):
        self._intType = value
    @property
    def IPaddr(self):
        return self._IPaddr
    @IPaddr.setter
    def IPaddr(self, value):
        self._IPaddr = value
    @property
    def aliasIPaddr(self):
        return self._aliasIPaddr
    @aliasIPaddr.setter
    def aliasIPaddr(self, value):
        self._aliasIPaddr = value
    @property
    def peerIPaddr(self):
        return self._peerIPaddr
    @peerIPaddr.setter
    def peerIPaddr(self, value):
        self._peerIPaddr = value
    @property
    def netmask(self):
        return self._netmask
    @netmask.setter
    def netmask(self, value):
        self._netmask = value
    @property
    def adminStatus(self):
        return self._adminStatus
    @adminStatus.setter
    def adminStatus(self, value):
        self._adminStatus =value
    @property
    def enableMACsticky(self):
        return self._enableMACsticky
    @enableMACsticky.setter
    def enableMACsticky(self, value):
        self._enableMACsticky = value
    @property
    def enableNormalization(self):
        return self._enableNormalization
    @enableNormalization.setter
    def enableNormalization(self, value):
        self._enableNormalization = value
    @property
    def enableIPv6(self):
        return self._enableIPv6
    @enableIPv6.setter
    def enableIPv6(self, value):
        self._enableIPv6 = value
    @property
    def ipv6GlobalIP(self):
        return self._ipv6GlobalIP
    @ipv6GlobalIP.setter
    def ipv6GlobalIP(self, value):
        self._ipv6GlobalIP = value
    @property
    def ipv6UniqueLocalAddr(self):
        return self._ipv6UniqueLocalAddr
    @ipv6UniqueLocalAddr.setter
    def ipv6UniqueLocalAddr(self, value):
        self._ipv6UniqueLocalAddr = value
    @property
    def ipv6LinkLocalAddr(self):
        return self._ipv6LinkLocalAddr
    @ipv6LinkLocalAddr.setter
    def ipv6LinkLocalAddr(self, value):
        self._ipv6LinkLocalAddr = value
    @property
    def ipv6PeerLinkLocalAddr(self):
        return self._ipv6PeerLinkLocalAddr
    @ipv6PeerLinkLocalAddr.setter
    def ipv6PeerLinkLocalAddr(self, value):
        self._ipv6PeerLinkLocalAddr = value
    @property
    def enableICMPguard(self):
        return self._enableICMPguard
    @enableICMPguard.setter
    def enableICMPguard(self, value):
        self._enableICMPguard = value
    @property
    def enableDHCPrelay(self):
        return self._enableDHCPrelay
    @enableDHCPrelay.setter
    def enableDHCPrelay(self, value):
        self._enableDHCPrelay = value
    @property
    def RPF(self):
        return self._RPF
    @RPF.setter
    def RPF(self, value):
        self._RPF = value
    @property
    def reassemblyTimeout(self):
        return self._reassemblyTimeout
    @reassemblyTimeout.setter
    def reassemblyTimeout(self, value):
        self._reassemblyTimeout = value
    @property
    def maxFragChainsAllowed(self):
        return self._maxFragChainsAllowed
    @maxFragChainsAllowed.setter
    def maxFragChainsAllowed(self, value):
        self._maxFragChainsAllowed = value
    @property
    def minFragMTUvalue(self):
        return self._minFragMTUvalue
    @minFragMTUvalue.setter
    def minFragMTUvalue(self, value):
        self._minFragMTUvalue = value
    @property
    def MTU(self):
        return self._MTU
    @MTU.setter
    def MTU(self, value):
        self._MTU = value
    @property
    def actionForIPheaderOptions(self):
        return self._actionForIPheaderOptions
    @actionForIPheaderOptions.setter
    def actionForIPheaderOptions(self, value):
        self._actionForIPheaderOptions = value
    @property
    def enableMACAddrAutogen(self):
        return self._enableMACAddrAutogen
    @enableMACAddrAutogen.setter
    def enableMACAddrAutogen(self, value):
        self._enableMACAddrAutogen = value
    @property
    def minTTLipHeaderValue(self):
        return self._minTTLipHeaderValue
    @minTTLipHeaderValue.setter
    def minTTLipHeaderValue(self, value):
        self._minTTLipHeaderValue = value
    @property
    def enableSynCookieThreshValue(self):
        return self._enableSynCookieThreshValue
    @enableSynCookieThreshValue.setter
    def enableSynCookieThreshValue(self, value):
        self._enableSynCookieThreshValue = value
    @property
    def actionForDBfit(self):
        return self._actionForDBfit
    @actionForDBfit.setter
    def actionForDBfit(self, value):
        self._actionForDBfit = value
    @property
    def ARPinspectType(self):
        return self._ARPinspectType
    @ARPinspectType.setter
    def ARPinspectType(self, value):
        self._ARPinspectType = value
    @property
    def UDPconfigCommands(self):
        return self._UDPconfigCommands
    @UDPconfigCommands.setter
    def UDPconfigCommands(self, value):
        self._UDPconfigCommands = value
    @property
    def secondaryIPgroups(self):
        return self._secondaryIPgroups
    @secondaryIPgroups.setter
    def secondaryIPgroups(self, value):
        self._secondaryIPgroups = value
    @property
    def inputPolicies(self):
        return self._inputPolicies
    @inputPolicies.setter
    def inputPolicies(self, value):
        self._inputPolicies = value
    @property
    def inputAccessGroup(self):
        return self._inputAccessGroup
    @inputAccessGroup.setter
    def inputAccessGroup(self, value):
        self._inputAccessGroup = value
    @property
    def outputAccessGroup(self):
        return self._outputAccessGroup
    @outputAccessGroup.setter
    def outputAccessGroup(self, value):
        self._outputAccessGroup = value
