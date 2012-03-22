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

from BaseDriver import BaseDriver
from Context import Context
from XmlSender import XmlSender

class AceDriver(BaseDriver):
    def __init__(self):
        pass
    
    
    def createRServer(self, context, rserver):
        if not bool(rserver.name): 
            return 'RSERVER NAME ERROR'

        XMLstr = "<rserver type='" + rserver.type.lower() + "' name='" + rserver.name + "'>\r\n"
        
        if bool(rserver.description): 
            XMLstr = XMLstr + "  <description descr-string='" + rserver.description + "'/>\r\n"
            
        if bool(rserver.IP):
            XMLstr = XMLstr + "  <ip_address node='address' "
            if (rserver.ipType.lower() == 'ipv4'):
                XMLstr = XMLstr + "ipv4-address='" 
            else:
                XMLstr = XMLstr + "ipv6-address='"
            XMLstr = XMLstr + rserver.IP + "'/>\r\n"
            
        XMLstr = XMLstr + "  <conn-limit max='" + str(rserver.maxCon) + "' min='" + str(rserver.minCon) + "'/>\r\n"
        
        if bool(rserver.rateConn):
            XMLstr = XMLstr + "  <rate-limit type='connection' value='" + str(rserver.rateConn) + "'/>\r\n"
            
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
                if (bool(probe.destIPv4v6)):
                    XMLstr = XMLstr + "  <ip_address address='" + probe.destIPv4v6 + "'"
                    if ((type != 'rtsp') and (type != 'sip-tcp') and (type != 'sip-udp')):
                        if bool(probe.isRouted):
                            XMLstr = XMLstr + " routing-option='routed'"
                    XMLstr = XMLstr + "/>\r\n"
                
            if (type == "dns"):
                if bool(probe.domainName):
                    XMLstr = XMLstr + "  <domain domain-name='" + probe.domainName + "'/>\r\n"
            
            if ((type == 'echo-udp') or (type == 'echo-tcp') or (type == 'finger')):
                if bool(probe.sendData):
                    XMLstr = XMLstr + "  <send-data data='" + probe.sendData + "'/>\r\n"

            if ((type == 'echo-tcp') or (type == 'finger') or (type == 'tcp')  or (type == 'rtsp')
                or (type == 'http') or (type == 'https') or (type == 'imap') or (type == 'pop')):
                    if bool(probe.openTimeout):
                        XMLstr = XMLstr + "  <open timeout='" + str(probe.openTimeout) + "'/>"
                    if bool(probe.tcpConnTerm):
                        XMLstr = XMLstr + "  <connection_term term='forced'/>\r\n"

            if ((type == 'http') or (type == 'https') or (type == 'imap') 
                or (type == 'pop') or (type == "radius")):
                    if (bool(probe.userName) and bool(probe.password)):
                        XMLstr = XMLstr + "  <credentials username='" + probe.userName + "' password='" + probe.password
                        if (type == 'radius'):
                            if bool(probe.userSecret):
                                XMLstr = XMLstr + "' secret='" + probe.userSecret
                        XMLstr = XMLstr + "'/>\r\n"

            if ((type == 'http') or (type == 'https')):
                if bool(probe.requestMethodType):
                    XMLstr = XMLstr + "  <request method='" + probe.requestMethodType + "' url='" + probe.requestHTTPurl + "'/>\r\n"
                    
                if bool(probe.appendPortHostTag):
                    XMLstr = XMLstr + "  <append-port-hosttag/>\r\n"
                
                if bool(probe.expectRegExp):
                    XMLstr = XMLstr + "  <expect_regex regex='" + probe.expectRegExp + "'"
                    if bool(probe.expectRegExpOffset):
                        XMLstr = XMLstr + " offset='" + str(probe.expectRegExpOffset) + "'"
                    XMLstr = XMLstr + "/>\r\n"
                    
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
                    
            # Need add sip-tcp, sip-udp, smtp, snmp, tcp, telnet, udp, vm


            
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
        
        
        
    
    
    def deleteProbe(self,  context,  probe):
        pass
    
    
    def createServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            return "SERVER FARM NAME ERROR"
        
        XMLstr = "<serverfarm type='" + serverfarm.type.lower() + "' name='" + serverfarm.name + "'>\r\n"
        
        if bool(serverfarm.description):
            XMLstr = XMLstr + "<description descr-string='" + serverfarm.description + "'/> \r\n"
        
        if bool(serverfarm.failAction):
            XMLstr = XMLstr + "<failaction failaction-type='" + serverfarm.failAction + "'/>\r\n"
        
        if bool(serverfarm.predictor): #Some predictors are may include additional parameters !
            XMLstr = XMLstr + "<predictor predictor-method='" + serverfarm.predictor + "'/>\r\n"
        
        for i in range(len(serverfarm.probes)):
            XMLstr = XMLstr + "<probe_sfarm probe-name='" + serverfarm.probes[i] + "'/>\r\n"
        
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
        if bool(rserver.rateConn):
            XMLstr=XMLstr+"<rate-limit type='connection' value='"+str(rserver.rateConn)+"'/>\r\n"
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
        #access-list permit ip any any - must be added !
        #!!! Before create we must perform a check for the presentce  access-list vip-acl remark... and its participation in vlan.
        
        
        # 1) Add a access-list
        XMLstr="<access-list id='vip-acl' line='"++"' config-type='extended' perm-value='permit' protocol-name='ip' src-type='any' host_dest-addr='"+vip.ip+"'/>\r\n"
        #2) Add a policy-map
        XMLstr=XMLstr+"<policy-map_lb type='loadbalance' match-type='first-match' pmap-name='"+vip.name+"-l7slb'>\r\n"
        XMLstr=XMLstr+"<class_pmap_lb match-cmap-default='class-default'>\r\n"
        XMLstr=XMLstr+"<serverfarm_pmap sfarm-name='"+sfarm.name+"'/>"
        XMLstr=XMLstr+"</class_pmap_lb>\r\n"
        XMLstr=XMLstr+"</policy-map_lb>\r\n"
        #3)Add a class-map
        XMLstr=XMLstr+"<class-map match-type='match-all' name='"+vip.name+"'>"
        XMLstr=XMLstr+"<match_virtual-addr seq-num='"++"' addr-type='virtual-address' ipv4-address='"+vip.ip+"' protocol-type='"+vip.proto.lower()+"'"
        if vip.proto.lower() != "any":
            XMLstr=XMLstr+" operator='eq' port-"+vip.proto.lower()+"-name='"+vip.Port+"'"
        XMLstr=XMLstr+"/>\r\n"
        XMLstr=XMLstr+"</class-map>\r\n"
        #4)Add a policy policy-map multi-match
        XMLstr=XMLstr+"<policy-map_multimatch match-type='multi-match' pmap-name='int2'>\r\n" # int2 ???
        XMLstr=XMLstr+"<class cmap-name='"+vip.name+"'>\r\n"
        XMLstr=XMLstr+"<loadbalance vip_config-type='inservice'/>\r\n"
        XMLstr=XMLstr+"<loadbalance policy='"+vip.name+"-l7slb'/>\r\n"
        XMLstr=XMLstr+"</class>"
        XMLstr=XMLstr+"</policy-map_multimatch>"
    
    
    def deleteVIP(self,  context,  vip):
        pass
    
