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

from balancer.loadbalancers.realserver import RealServer
from balancer.BaseDriver import BaseDriver

class Context(BaseContext):
    pass

class AceDriver(BaseDriver):
    def __init__(self):
        pass
    
    def createRServer(self, obj):
        TMP="<rserver "
        TMP=TMP+"type='"+obj.type+"' name='"+obj.name+"'>\n"
        if obj.type == "host":
            TMP=TMP+"<ip address node='address' ipv4-address='"+obj.IP+"'/>\n"
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
        return TMP

    def deleteRServer(self, obj):
        TMP="<rserver sense='no' type='host' name='" + obj.name + "'></rserver>\n"
        return TMP

    def createServerFarm(self, obj):
        TMP="<SFarm>\n"
        TMP=TMP+"rsever "+obj.type+" "+obj.name+"\n"
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
        TMP=TMP+"predictor"+obj.predictor #Check it !!!
        TMP="<\\SFarm>\n"
        
    def addRServerToSF(self, obj):
        TMP="<RealServer>\n"
        pass
    
    def deleteRServerFromSF(self, obj):
        pass
        
