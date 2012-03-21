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

        XMLstr = "<rserver type='" + rserver.type.lower() + "' name='" + rserver.name + "'>\r\n"
        
        if bool(rserver.description): 
            XMLstr = XMLstr + "  <description descr-string='" + rserver.description + "'/>\r\n"
            
        if bool(rserver.IP):
            XMLstr = XMLstr + "  <ip_address node='address' ipv4-address='" + rserver.IP + "'/>\r\n"
            
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




    def createServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name):
            return "ERROR"
        
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
        


    def deleteRServer(self, context, rserver):
        if not bool(rserver.name): 
            return 'ERROR'
            
        XMLstr = "<rserver sense='no' name='" + rserver.name + "'></rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)    
        
        
        
    def deleteServerFarm(self,  context,  serverfarm):
        if not bool(serverfarm.name): 
            return 'ERROR'

        XMLstr = "<serverfarm sense='no' name='" + serverfarm.name + "'></serverfarm>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr) 
        
        
        
    def activateRServer(self,  context,  serverfarm,  rserver):
        if not bool(rserver.name): 
            return 'ERROR'

        XMLstr = "<rserver name='" + rserver.name + "'>\r\n  <inservice/>\r\n</rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
        
        
        
    def suspendRServer(self,  context,  serverfarm,  rserver):
        if not bool(rserver.name): 
            return 'ERROR'

        XMLstr = "<rserver name='" + rserver.name + "'>\r\n  <inservice sense='no'/>\r\n</rserver>"
        
        s = XmlSender(context)
        return s.deployConfig(context, XMLstr)
