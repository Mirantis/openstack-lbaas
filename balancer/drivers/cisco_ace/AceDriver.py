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
            return 'ERROR'

        XMLstr = "<rserver "
        XMLstr = XMLstr + "type='" + rserver.type.lower() + "' name='" + rserver.name + "'>\r\n"
        if bool(rserver.IP):
            XMLstr = XMLstr + "  <ip_address node='address' ipv4-address='" + rserver.IP + "'/>\r\n"
        if bool(rserver.description): 
            XMLstr = XMLstr + "  <description descr-string='" + rserver.description + "'/>\r\n"
        if bool(rserver.maxCon):
            pass

        XMLstr = XMLstr + "</rserver>"
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)    

        q = """
            if obj.failOnAll != None: TMP=TMP+"fail-on-all\n"
        TMP=TMP+"conn-limit max "+str(obj.maxCon)+" min "+str(obj.minCon)+"\n"
        TMP=TMP+"weight "+str(obj.weight)+"\n"
        TMP=TMP+"description "+obj.description+"\n"
        if obj.type == "redirect" and obj.webHostRedir != "":
            TMP=TMP+"webhost-redirection "+obj.webHostRedir+"\n"
        if obj.rateBandwidth != "":
            TMP=TMP+"rate-limit bandwidth "+str(obj.rateBandwidth)+"\n"
        if obj.rateConn != "":
            TMP=TMP+"rate-limit connection "+str(obj.rateConn)+"\n"
        if obj.state != "":
            TMP=TMP+obj.state+"\n"
        for i in range(len(obj.probes)):
            TMP=TMP+"probe "+obj.probes[i]+"\n"
        TMP=TMP+"<inservice/></rserver>\n"
        """

    def createServerFarm(self, obj):
        TMP="<SFarm>\n"
        TMP=TMP+"sfarm "+obj.type+" "+obj.name+"\n"
        for i in range(len(obj.probes)):
            TMP=TMP+"probe "+obj.probes[i]+"\n"
        if obj.failAction != None:
            TMP=TMP+"failaction "+obj.failAction+"\n"
        TMP=TMP+"description "+obj.description+"\n"
        if obj.type == "host":
            if obj.dynamicWorkloadScale != None: # Need to upgrade (may include VM's)
                TMP=TMP+"dws "+obj.failAction+"\n"
            if obj.failOnAll != None: 
                TMP=TMP+"fail-on-all\n"
            if obj.inbandHealthCheck == "remove":
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"remove"+obj.connFailureThreshCount
                if obj.resetTimeout != None:
                    TMP=TMP+" reset"+obj.resetTimeout
                if obj.resumeService != None:
                    TMP=TMP+" resume-service"+obj.resumeService
                TMP=TMP+"\n"
            elif obj.inbandHealthCheck == "log":
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"remove"+obj.connFailureThreshCount+"\n"
            else:
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"\n"
            if obj.transparent != None:
                TMP=TMP+"transparent\n"
            if (obj.partialThreshPercentage != None) and (obj.backInservice != None):
                TMP=TMP+"partial-threshold "+obj.partialThreshPercentage+" back-inservice "+obj.backInservice+"\n"
        TMP=TMP+"predictor"+obj.predictor #Now correct for RoundRobin. Some predictors are may include additional parameters !
        TMP="<\\SFarm>\n"
        return TMP
        
    def addRServerToSF(self, obj): 
        TMP="<serverfarm name='"+obj.name+"'>\n"
        for i in range(len(obj.rservers)):
            TMP=TMP+"<rserver name="+obj.probes[i]+"\\\n"
            TMP=TMP+"<inservice sense='inservice'\\>\n"
        TMP=TMP+"<//serverfarm>\n"
        return TMP
    
    def createProbe(self,  context,  probe): #Now, correct only  for ICMP and partially dor HTTP
        TMP="<probe type='"+probe.type+"' name='"+probe.name+"'>\n"
        if probe.description != None: 
            TMP=TMP+"<description>"+probe.description+"</description>\n"
        if probe.failDetect != None:
            TMP=TMP+"<faildetect>"+str(probe.failDetect)+"</faildetect>\n"
        if probe.probeInterval != None:
            TMP=TMP+"<interval>"+str(probe.probeInterval)+"</interval>\n"
        if probe.passDetectInterval != None:
            TMP=TMP+"<passdetect interval>"+str(probe.passDetectInterval)+"</passdetect interval>\n"
        if probe.type == "HTTP": #Necessary add ._method and ._ url to probe.py 
            if probe.port != None:
                TMP=TMP+"<port>"+str(probe.port)+"</port>\n"
            TMP=TMP+"<reques method='"+probe.method+"'"
            if probe.url != None:
                TMP=TMP+"'"+probe.url+"'"
            TMP=TMP+"/>\n"
        
        #More settings
        if probe.passDetectCount != None:
            TMP=TMP+"<passdetect count>"+str(probe.passDetectCount)+"</passdetect count>\n"
        if probe.receiveTimeout != None:
            TMP=TMP+"<receive>"+str(probe.receiveTimeout)+"</receive>\n"
        if probe.destip != None: #Necessary add ._destip to probe.py
            TMP=TMP+"<ip address='"+probe.destip+"'"
            if probe.isRouted != None:
                TMP=TMP+" type='"+probe.isRouted+"'"
            TMP=TMP+"/>\n"
        
        TMP=TMP+"</probe>"
        return TMP
    
    def attachProbeToSF(self,  context,  serverfarm,  probe):
        TMP="<serverfarm name='"+serverfarm.name+"'>\n"
        TMP=TMP+"<probe name='"+probe.name+"'/>\n"
        TMP=TMP+"</serverfarm>"
    
    def createVIP(self,  context, vip,  sfarm): 
        #access-list permit ip any any - must be added !
        TMP="<policy map type='loadbalance' conf='first-match' name='"+vip.name+"-l7slb'>\n"
        TMP=TMP+"<class name='class-default'>\n"
        TMP=TMP+"<serverfarm name='"+sfarm.name+"'/>\n"
        TMP=TMP+"</class>\n"
        TMP=TMP+"</policy map>\n"
        
        TMP=TMP+"<class map type='match-all' name='"+vip.name+"'>\n"
        TMP=TMP+"<param line='2' criteria='match virtual-adress "+vip.ip+" "+vip.virtIPmask+"'/>\n" #How define <line number> ?
        TMP=TMP+"</class map>"
        
        TMP=TMP+"<policy map type='multi-match' name='int"+vip.id+"'>\n"
        TMP=TMP+"<class name='"+vip.name+"'>"
        TMP=TMP+"<loadbalance policy name='"+vip.name+"-l7slb'>\n"
        TMP=TMP+"<loadbalance vip inservice'>\n"
        TMP=TMP+"</class>"
        TMP=TMP+"</policy map>"
        

    def deleteRServer(self, obj):
        TMP="<rserver sense='no' type='host' name='" + obj.name + "'></rserver>\n"
        return TMP
