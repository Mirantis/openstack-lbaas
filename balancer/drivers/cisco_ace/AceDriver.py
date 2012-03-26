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

import md5
import logging

from balancer.drivers.BaseDriver import BaseDriver
from balancer.drivers.cisco_ace.Context import Context
from balancer.drivers.cisco_ace.XmlSender import XmlSender


logger = logging.getLogger(__name__)

class AceDriver(BaseDriver):
    def __init__(self):
        pass
    
    def getContext (self,  dev):
        logger.debug("Creating conext with params: IP %s, Port: %s" %(dev.ip,  dev.port))
        con = Context(dev.ip, dev.port, dev.user,  dev.password)
        return con
    
    def createRServer(self, context, rserver):
        logger.debug("Creating Rserver")
        if not bool(rserver.name): 
            logger.error("Can't find rserver name")
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver type='" + rserver.type.lower() + "' name='" + rserver.name + "'>\r\n"
        
        if bool(rserver.description): 
            XMLstr = XMLstr + "  <description descr-string='" + rserver.description + "'/>\r\n"

        if bool(rserver.address):
            XMLstr = XMLstr + "  <ip_address node='address' "
            if (rserver.ipType.lower() == 'ipv4'):
                XMLstr = XMLstr + "ipv4-address='" 
            else:
                XMLstr = XMLstr + "ipv6-address='"
            XMLstr = XMLstr + rserver.address + "'/>\r\n"
            
        if (bool(rserver.maxCon) and bool(rserver.minCon)):
            XMLstr = XMLstr + "  <conn-limit max='" + str(rserver.maxCon) + "' min='" + str(rserver.minCon) + "'/>\r\n"
        
        if bool(rserver.rateConnection):
            XMLstr = XMLstr + "  <rate-limit type='connection' value='" + str(rserver.rateConnection) + "'/>\r\n"
            
        if bool(rserver.rateBandwidth):
            XMLstr = XMLstr + "  <rate-limit type='bandwidth' value='" + str(rserver.rateBandwidth) + "'/>\r\n"        

        if bool(rserver.failOnAll):
            XMLstr = XMLstr + "  <fail-on-all/>\r\n"

        if (rserver.type.lower() == "host"):
            XMLstr = XMLstr + "  <weight value='" + str(rserver.weight) + "'/>\r\n"
            
        if bool(rserver.webHostRedir):
            XMLstr = XMLstr + "  <webhost-redirection relocation-string='" + rserver.webHostRedir + "'/>\r\n" 
            # without parameter  redirection-code=

        if (rserver.state == "In Service"):
            XMLstr = XMLstr + "  <inservice/>\r\n"
            
        XMLstr = XMLstr + "</rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)    
    
    
    def deleteRServer(self, context, rserver):
        if not bool(rserver.name): 
            return 'RSERVER NAME ERROR'
        
        XMLstr = "<rserver sense='no' name='" + rserver.name + "'></rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)  
    
    
    def activateRServer(self,  context,  serverfarm,  rserver):
        if not bool(rserver.name): 
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver name='" + rserver.name + "'>\r\n  <inservice/>\r\n</rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
    
    
    def suspendRServer(self,  context,  serverfarm,  rserver):
        if not bool(rserver.name): 
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver name='" + rserver.name + "'>\r\n  <inservice sense='no'/>\r\n</rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
    
    
    
    
    def createProbe(self,  context,  probe):
        if not bool(probe.name): 
            return 'PROBE NAME ERROR'
        type = probe.type.lower()
        if type == "connect":
            type = "tcp"
        # Rport need to add for SIP-UDP Probe
        # sendData need to add for TCP Probe
        
        probes_with_send_data = ['echo-udp',  'echo-tcp',  'finger',  'tcp',  'udp']
        probes_with_timeout = ['echo-tcp',  'finger',  'tcp',  'rtsp',  'http',  'https',  'imap',  'pop',  'sip-tcp',  'smtp',  'telnet']
        probes_with_credentials = ['http',  'https',  'imap',  'pop',  'radius']
        probes_with_regex = ['http',  'https',  'sip-tcp',  'sup-udp',  'tcp',  'udp']
        
        if ((type != 'echo-tcp') and (type != 'echo-udp')):
            XMLstr = "<probe_" + type + " type='"  + type + "' name='" + probe.name + "'>\r\n"
        else:
            XMLstr = "<probe_echo type='echo' conn-type='"
            if (type == 'echo-tcp'):
                XMLstr = XMLstr + "tcp' name='"
            else:
                XMLstr = XMLstr + "udp' name='"
            XMLstr = XMLstr + probe.name + "'>\r\n"
    
        if bool(probe.description): 
            XMLstr = XMLstr + "  <description descr-string='" + probe.description + "'/>\r\n"
                
        if bool(probe.probeInterval):
            XMLstr = XMLstr + "  <interval value='" + str(probe.probeInterval) + "'/>\r\n"
        
        if (type != 'vm'):
            if bool(probe.passDetectInterval):
                XMLstr = XMLstr + "  <passdetect interval='" + str(probe.passDetectInterval) + "'/>\r\n"
                
            if bool(probe.passDetectCount):
                XMLstr = XMLstr + "  <passdetect count='" + str(probe.passDetectCount) + "'/>\r\n"
            
            if bool(probe.failDetect):
                XMLstr = XMLstr + "  <faildetect retry-count='" + str(probe.failDetect) + "'/>\r\n"
            
            if bool(probe.receiveTimeout):
                XMLstr = XMLstr + "  <receive timeout='" + str(probe.receiveTimeout) + "'/>\r\n"
            
            if ((type != 'icmp') and bool(probe.port)):
                XMLstr = XMLstr + "  <port value='" + str(probe.port) + "'/>\r\n"

            if (type != 'scripted'):
                if (bool(probe.destIP)):
                    XMLstr = XMLstr + "  <ip_address address='" + probe.destIP + "'"
                    if ((type != 'rtsp') and (type != 'sip-tcp') and (type != 'sip-udp')):
                        if bool(probe.isRouted):
                            XMLstr = XMLstr + " routing-option='routed'"
                    XMLstr = XMLstr + "/>\r\n"
                
            if (type == "dns"):
                if bool(probe.domainName):
                    XMLstr = XMLstr + "  <domain domain-name='" + probe.domainName + "'/>\r\n"
            
            if (probes_with_send_data.count(type) > 0):
                if bool(probe.sendData):
                    XMLstr = XMLstr + "  <send-data data='" + probe.sendData + "'/>\r\n"

            if (probes_with_timeout.count(type) > 0):
                if bool(probe.openTimeout):
                    XMLstr = XMLstr + "  <open timeout='" + str(probe.openTimeout) + "'/>"
                if bool(probe.tcpConnTerm):
                    XMLstr = XMLstr + "  <connection_term term='forced'/>\r\n"

            if (probes_with_credentials.count(type) > 0):
                if (bool(probe.userName) and bool(probe.password)):
                    XMLstr = XMLstr + "  <credentials username='" + probe.userName + "' password='" + probe.password
                    if (type == 'radius'):
                        if bool(probe.userSecret):
                            XMLstr = XMLstr + "' secret='" + probe.userSecret
                    XMLstr = XMLstr + "'/>\r\n"

            if (probes_with_regex.count(type) > 0):
                    if bool(probe.expectRegExp):
                        XMLstr = XMLstr + "  <expect_regex regex='" + probe.expectRegExp + "'"
                        if bool(probe.expectRegExpOffset):
                            XMLstr = XMLstr + " offset='" + str(probe.expectRegExpOffset) + "'"
                        XMLstr = XMLstr + "/>\r\n"

            if ((type == 'http') or (type == 'https')):
                if bool(probe.requestMethodType):
                    XMLstr = XMLstr + "  <request method='" + probe.requestMethodType + "' url='" + probe.requestHTTPurl + "'/>\r\n"
                    
                if bool(probe.appendPortHostTag):
                    XMLstr = XMLstr + "  <append-port-hosttag/>\r\n"
                    
                if bool(probe.hash):
                    XMLstr = XMLstr + "  <hash"
                    if bool(probe.hashString):
                        XMLstr = XMLstr + " hash-string='" + probe.hashString + "'"
                    XMLstr = XMLstr + "/>\r\n"

                if (type == 'https'):
                    if bool(probe.cipher):
                        XMLstr = XMLstr + "  <ssl cipher='" + probe.cipher + "'/>\r\n"
                    if bool(probe.SSLversion):
                        XMLstr = XMLstr + "  <ssl version='" + probe.SSLversion + "'/>\r\n"
                        
            if ((type == 'pop') or (type == 'imap')):
                if bool(probe.requestCommand):
                    XMLstr = XMLstr + "  <request command='" + probe.requestCommand + "'/>\r\n"
                if (type == 'imap'):
                    if bool(probe.maibox):
                        XMLstr = XMLstr + "  <credentials mailbox='" + probe.maibox + "'/>\r\n"

            if (type == 'radius'):
                if bool(probe.NASIPaddr):
                    XMLstr = XMLstr + "  <nas ip_address='" + probe.NASIPaddr + "'/>\r\n"
                    
            if (type == 'rtsp'):
                if bool(probe.requareHeaderValue):
                    XMLstr = XMLstr + "  <header header-name='Require' header-value='" + probe.requareHeaderValue + "'/>\r\n"
                    
                if bool(probe.proxyRequareHeaderValue):
                    XMLstr = XMLstr + "  <header header-name='Proxy-Require' header-value='" + probe.proxyRequareHeaderValue + "'/>\r\n"
                    
                if bool(probe.requestURL):
                    XMLstr = XMLstr + "  <request "
                    if bool(probe.requestMethodType):
                        XMLstr = XMLstr + "  method='" + probe.requestMethodType + "' "
                    XMLstr = XMLstr + "url='" + probe.requestURL + "'/>\r\n"
            
            # Need add download script section for this type
            if (type == 'scripted'):
                if bool(probe.scriptName):
                    XMLstr = XMLstr + "  <script_elem script-name='" + probe.scriptName
                    if bool(probe.scriptArgv):
                       XMLstr = XMLstr + "' script-arguments='" + probe.scriptArgv
                    XMLstr = XMLstr + "'/>\r\n"
            
            if ((type == 'sip-udp') and bool(probe.Rport)):
                XMLstr = XMLstr + "  <rport type='enable'/>\r\n"
                
            if (type == 'snmp'):
                if bool(probe.SNMPver):
                    XMLstr = XMLstr + "  <version value='" + probe.SNMPver + "'/>\r\n"
                    if bool(probe.SNMPComm):
                        XMLstr = XMLstr + "  <community community-string='" + probe.SNMPComm + "'/>\r\n"
            
        else:   # for type == vm
            if bool(probe.VMControllerName):
                XMLstr = XMLstr + "  <vm-controller name='" + probe.VMControllerName + "'/>\r\n"
                if (bool(probe.maxCPUburstThresh) or bool(probe.minCPUburstThresh)):
                    XMLstr = XMLstr + "  <load type='cpu' param='burst-threshold'"
                    if bool(probe.maxCPUburstThresh):
                        XMLstr = XMLstr + " max='" + probe.maxCPUburstThresh + "'"
                    if bool(probe.minCPUburstThresh):
                        XMLstr = XMLstr + " min='" + probe.minCPUburstThresh + "'"
                    XMLstr = XMLstr + "/>\r\n"
                if (bool(probe.maxMemBurstThresh) or bool(probe.minMemBurstThresh)):
                    XMLstr = XMLstr + "  <load type='mem' param='burst-threshold'"
                    if bool(probe.maxMemBurstThresh):
                        XMLstr = XMLstr + " max='" + probe.maxMemBurstThresh + "'"
                    if bool(probe.minMemBurstThresh):
                        XMLstr = XMLstr + " min='" + probe.minMemBurstThresh + "'"
                    XMLstr = XMLstr + "/>\r\n"
            
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
        
        
        
    
    
    def deleteProbe(self,  context,  probe):
        if not bool(probe.name): 
            return 'PROBE NAME ERROR'
        type = probe.type.lower()

        if ((type != 'echo-tcp') and (type != 'echo-udp')):
            XMLstr = "<probe_" + type + " type='"  + type + "' name='" + probe.name + "' sense='no'>\r\n"
        else:
            XMLstr = "<probe_echo type='echo' conn-type='"
            if (type == 'echo-tcp'):
                XMLstr = XMLstr + "tcp' name='"
            else:
                XMLstr = XMLstr + "udp' name='"
            XMLstr = XMLstr + probe.name + "' sense='no'>\r\n"
            
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
        
    
    
    def createServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            return "SERVER FARM NAME ERROR"
        
        XMLstr = "<serverfarm type='" + serverfarm.type.lower() + "' name='" + serverfarm.name + "'>\r\n"
        
        if bool(serverfarm.description):
            XMLstr = XMLstr + "<description descr-string='" + serverfarm.description + "'/> \r\n"
        
        if bool(serverfarm.failAction):
            XMLstr = XMLstr + "<failaction failaction-type='" + serverfarm.failAction + "'/>\r\n"
        
        if bool(serverfarm._predictor): #Some predictors are may include additional parameters !
            XMLstr = XMLstr + "<predictor predictor-method='" + serverfarm._predictor.type.lower() + "'/>\r\n"
        
        #for probe in serverfarm._probes:
         #   XMLstr = XMLstr + "<probe_sfarm probe-name='" + probe.name + "'/>\r\n"
        
        if serverfarm.type.lower() == "host":
            if bool(serverfarm.failOnAll): 
                XMLstr = XMLstr + "<probe_sfarm probe-name='fail-on-all'/>\r\n"
            
            if bool(serverfarm.transparent):
                XMLstr = XMLstr + "<transparent/>\r\n"
            
            if bool(serverfarm.partialThreshPercentage) and bool(serverfarm.backInservice):
                XMLstr = XMLstr + "<partial-threshold value='" + serverfarm.partialThreshPercentage + "' back-inservice='" + serverfarm.backInservice + "'/>\r\n"
            
            if bool(serverfarm.inbandHealthCheck):
                XMLstr = XMLstr + "<inband-health check='" + serverfarm.inbandHealthCheck + "'"
                if serverfarm.inbandHealthCheck.lower == "log":
                    XMLstr = XMLstr + "threshold='" + str(serverfarm.connFailureThreshCount) + "' reset='" + str(serverfarm.resetTimeout) + "'" #Do deploy if  resetTimeout='' ?
                    
                if serverfarm.inbandHealthCheck.lower == "remove":
                    XMLstr=XMLstr+"threshold='"+str(serverfarm.connFailureThreshCount)+"' reset='"+str(serverfarm.resetTimeout)+"'  resume-service='"+str(serverfarm.resumeService)+"'" #Do deploy if  resumeService='' ?
                XMLstr=XMLstr+"/>\r\n"
            
            if bool(serverfarm.dynamicWorkloadScale): # Need to upgrade (may include VM's)
                XMLstr = XMLstr + "<dws type='" + serverfarm.failAction + "'/>\r\n"
        
        XMLstr = XMLstr + "</serverfarm>"
        
        res = XmlSender(context)
        return res.deployConfig(context, XMLstr) 
    
    
    def deleteServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name): 
            return 'SERVER FARM NAME ERROR'

        XMLstr = "<serverfarm sense='no' name='" + serverfarm.name + "'></serverfarm>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr) 
    
    
    def addRServerToSF(self,  context,  serverfarm,  rserver): #rserver in sfarm may include many parameters !
        if not bool(serverfarm.name) or not bool(rserver.name):
            return "ERROR"
        
        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr=XMLstr+" <rserver_sfarm name='"+rserver.name+"'"
        if bool(rserver.port):
            XMLstr=XMLstr+" port='"+rserver.port+"'"
        XMLstr=XMLstr+">\r\n"
        if bool(rserver.weight):
            XMLstr=XMLstr+"<weight value='"+str(rserver.weight)+"'/>\r\n"
        if bool(rserver.backupRS):
            XMLstr=XMLstr+"<backup-rserver rserver-name='"+rserver.backupRS+"'"
            if bool(rserver.backupRSport):
                XMLstr=XMLstr+" port='"+rserver.backupRSport+"'"
            XMLstr=XMLstr+"/>\r\n"
        if bool(rserver.maxCon) and bool(rserver.minCon):
            XMLstr=XMLstr+"<conn-limit max='"+str(rserver.maxCon)+"' min='"+str(rserver.minCon)+"'/>\r\n"
        if bool(rserver.rateConnection):
            XMLstr=XMLstr+"<rate-limit type='connection' value='"+str(rserver.rateConnection)+"'/>\r\n"
        if bool(rserver.rateBandwidth):
            XMLstr=XMLstr+"<rate-limit type='bandwidth' value='"+str(rserver.rateBandwidth)+"'/>\r\n"
        if bool(rserver.cookieStr):
            XMLstr=XMLstr+"<cookie-string value='"+rserver.cookieStr+"'/>\r\n"
        for i in range(len(rserver.probes)):
            XMLstr=XMLstr+"<probe_sfarm probe-name='"+rserver.probes[i]+"'/>\r\n"
        if bool(rserver.failOnAll):
            XMLstr=XMLstr+"<probe_sfarm probe-name='fail-on-all'/>"
        if bool(rserver.state):
            if rserver.state.lower() == "inservice":
                XMLstr=XMLstr+"<inservice/>\r\n"
            if rserver.state.lower() == "standby":
                XMLstr=XMLstr+"<inservice mode='"+rserver.state.lower()+"'/>\r\n"
            if rserver.state.lower() == "outofservice":
                XMLstr=XMLstr+"<inservice sense='no'/>\r\n"
        XMLstr=XMLstr+"</rserver_sfarm>\r\n"
        XMLstr=XMLstr+"</serverfarm>"
        
        res = XmlSender(context)
        return res.deployConfig(context, XMLstr)
    
    
    def deleteRServerFromSF(self,  context,  serverfarm,  rserver):
        if not bool(serverfarm.name) or not bool(rserver.name):
            return "ERROR"
        
        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr=XMLstr+"<rserver_sfarm sense='no' name='"+rserver.name+"'"
        if bool(rserver.port):
            XMLstr=XMLstr+" port='"+rserver.port+"'"
        XMLstr=XMLstr+">\r\n"
        XMLstr=XMLstr+"</rserver_sfarm>\r\n"
        XMLstr=XMLstr+"</serverfarm>"
        
        res = XmlSender(context)
        return res.deployConfig(context, XMLstr)
    
    
    def addProbeToSF(self,  context,  serverfarm,  probe):
        if not bool(serverfarm.name) or not bool(probe.name):
            return "ERROR"
        
        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr=XMLstr+" <probe_sfarm probe-name='"+probe.name+"'/>\r\n"
        XMLstr=XMLstr+"</serverfarm>"
        
        res = XmlSender(context)
        return res.deployConfig(context, XMLstr)
    
    
    def deleteProbeFromSF (elf,  context,  serverfarm,  probe):
        if not bool(serverfarm.name) or not bool(probe.name):
            return "ERROR"
        
        XMLstr = "<serverfarm name='" + serverfarm.name + "'>\r\n"
        XMLstr=XMLstr+" <probe_sfarm sense='no' probe-name='"+probe.name+"'/>\r\n"
        XMLstr=XMLstr+"</serverfarm>"
        
        res = XmlSender(context)
        return res.deployConfig(context, XMLstr)
    
    
    def createStickiness(self,  context,  vip,  sticky):
        pass
    
    
    def deleteStickiness(self,  context,  vip,  sticky):
        pass
    
    
    def createVIP(self,  context, vip,  sfarm): 
        if not bool(vip.name) or not bool(vip.name) or not bool(vip.address) :
            return "ERROR"
        
        sn = "2"
        if bool(vip.allVLANs):
            pmap = "global"
        else:
            #vip.VLAN.sort()
            pmap = "int-"
            s = vip.VLAN
            m = md5.new(s).hexdigest()
            pmap = pmap + m
        
        tmp = ""
        res = XmlSender(context)
        #! Before create we must perform a check for the presentce  access-list vip-acl remark... and its participation in vlan.
        #<access-list id='vip-acl' config-type='remark' comment='Created to permit IP traffic to VIP.'/>
        
        # 1) Add a access-list
        XMLstr = "<access-list id='vip-acl' config-type='extended' perm-value='permit' protocol-name='ip' src-type='any' host_dest-addr='" + vip.address + "'/>\r\n"
        
        #2) Add a policy-map
        if vip.appProto.lower() == "other" or vip.appProto.lower() == "http":
            vip.appProto = ""
        else:
            vip.appProto = "_" + vip.appProto.lower()
        
        XMLstr = XMLstr + "<policy-map_lb type='loadbalance" + vip.appProto + "' match-type='first-match' pmap-name='"+vip.name+"-l7slb'>\r\n"
        XMLstr = XMLstr + "<class_pmap_lb match-cmap-default='class-default'>\r\n"
        XMLstr = XMLstr + "<serverfarm_pmap sfarm-name='" + sfarm.name + "'"
        if bool(vip.backupServerFarm):
            XMLstr = XMLstr + " backup-name='" + vip.backupServerFarm + "'"
        XMLstr = XMLstr + "/>\r\n"
        XMLstr = XMLstr + "</class_pmap_lb>\r\n"
        XMLstr = XMLstr + "</policy-map_lb>\r\n"
        
        #3)Add a class-map
        XMLstr = XMLstr + "<class-map match-type='match-all' name='" + vip.name + "'>\r\n"
        XMLstr = XMLstr + "<match_virtual-addr seq-num='" + sn + "' addr-type='virtual-address' ipv4-address='" + vip.address + "' net-mask='" + str(vip.mask) + "'"
        XMLstr = XMLstr + " protocol-type='" + vip.proto.lower() + "'"
        if vip.proto.lower() != "any":
            XMLstr = XMLstr + " operator='eq' port-" + vip.proto.lower() + "-name='" + str(vip.port) + "'"
        XMLstr = XMLstr + "/>\r\n"
        XMLstr = XMLstr + "</class-map>\r\n"
        
        #4)Add a policy-map (multimatch) with class-map
        XMLstr = XMLstr + "<policy-map_multimatch match-type='multi-match' pmap-name='" + pmap + "'>\r\n"
        XMLstr = XMLstr + "<class cmap-name='" + vip.name + "'>\r\n"
        if bool(vip.status):
            XMLstr = XMLstr + "<loadbalance vip_config-type='" + vip.status.lower() + "'/>\r\n"
        XMLstr = XMLstr + "<loadbalance policy='" + vip.name + "-l7slb'/>\r\n"
        XMLstr = XMLstr + "</class>\r\n"
        XMLstr = XMLstr + "</policy-map_multimatch>\r\n"
        
        tmp = tmp + res.deployConfig(context, XMLstr)
        
        #5)Add service-policy for necessary vlans
        if bool(vip.allVLANs):
            XMLstr = "<service-policy type='input' name='" + pmap + "'/>"
        else:
            XMLstr = ""
            for i in vip.VLAN:
                XMLstr = XMLstr + "<interface type='vlan' number='" + str(i) + "'>\r\n"
                XMLstr = XMLstr + "<service-policy type='input' name='" + pmap + "'/>\r\n"
                XMLstr = XMLstr + "</interface>"
        
        tmp = tmp + res.deployConfig(context, XMLstr)
        
        #6)Add vip-acl to each VLANs (Appear error during repeated deploy)
        if bool(vip.allVLANs):
            pass
        else:
            XMLstr = ""
            for i in vip.VLAN:
                XMLstr = XMLstr + "<interface type='vlan' number='" + str(i) + "'>\r\n"
                XMLstr = XMLstr + "<access-group access-type='input' name='vip-acl'/>\r\n"
                XMLstr = XMLstr + "</interface>"
                res.deployConfig(context, XMLstr)
        
        return tmp
    
    def deleteVIP(self,  context,  vip):
        if bool(vip.allVLANs):
            pmap = "global"
        else:
            #vip.VLAN.sort()
            pmap = "int-"
            s = vip.VLAN
            m = md5.new(s).hexdigest()
            pmap = pmap + m
        
        res = XmlSender(context)
        
        XMLstr = "<policy-map_multimatch match-type='multi-match' pmap-name='" + pmap + "'>\r\n"
        XMLstr = XMLstr + "<class sense='no' cmap-name='" + vip.name + "'>\r\n"
        XMLstr = XMLstr + "</class>\r\n"
        XMLstr = XMLstr + "</policy-map_multimatch>\r\n"
        
        tmp = res.deployConfig(context, XMLstr)
        
        #3) Delete policy-map, class-map and access-list
        if vip.appProto.lower() == "other" or vip.appProto.lower() == "http":
            vip.appProto = ""
        else:
            vip.appProto = "_" + vip.appProto.lower()
        XMLstr = "<policy-map_lb sense='no' type='loadbalance" + vip.appProto
        XMLstr = XMLstr + "' match-type='first-match' pmap-name='" + vip.name + "-l7slb'>\r\n"
        XMLstr = XMLstr + "</policy-map_lb>\r\n"
        
        XMLstr = XMLstr + "<class-map sense='no' match-type='match-all' name='" + vip.name + "'>\r\n"
        XMLstr = XMLstr + "</class-map>\r\n"
        
        XMLstr = XMLstr + "<access-list sense='no' id='vip-acl' config-type='extended' perm-value='permit' " 
        XMLstr = XMLstr + "protocol-name='ip' src-type='any' host_dest-addr='" + vip.address + "'/>\r\n"
        
        tmp = res.deployConfig(context, XMLstr)

        last_policy_map = ''
        if (last_policy_map == 'YES'):
            # Remove service-policy from VLANs (Perform if deleted last VIP with it service-policy)
            if bool(vip.allVLANs):
                XMLstr = "<service-policy sense='no' type='input' name='" + pmap + "'/>"
            else:
                XMLstr = ""
                for i in vip.VLAN:
                    XMLstr = XMLstr + "<interface type='vlan' number='" + str(i) + "'>\r\n"
                    XMLstr = XMLstr + "<service-policy sense='no' type='input' name='" + pmap + "'/>\r\n"
                    XMLstr = XMLstr + "</interface>"
            tmp = res.deployConfig(context, XMLstr)

            # Delete class-map from policy-map
            XMLstr = "<policy-map_multimatch sense='no' match-type='multi-match' pmap-name='" + pmap + "'>\r\n"
            XMLstr = XMLstr + "</policy-map_multimatch>\r\n"
            tmp = res.deployConfig(context, XMLstr)
    
