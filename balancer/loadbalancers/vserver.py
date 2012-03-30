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




from openstack.common import exception
#from balancer.loadbalancers.command import BaseCommand
import balancer.storage.storage 

import loadbalancer
import predictor
import probe
import realserver
import serverfarm
import vlan
import virtualserver

logger = logging.getLogger(__name__)


class Balancer():
    def __init__(self):

        """ This member contains LoadBalancer object """
        self.lb = None
        self.sf = None
        self.rs = []
        self.probes = []
        self.vips = []
        
    def parseParams(self, params):
        
        if (params.has_key('lb')):
            lb = params['lb']
        else:
            lb = loadbalancer.LoadBalancer()
        lb.loadFromDict(params)
        self.lb = lb
        nodes = params.get('nodes',  None)
        sf = serverfarm.ServerFarm()
        sf.lb_id = lb.id
        sf._predictor = createPredictor(lb.algorithm)
        sf._predictor.sf_id = sf.id
        sf.name = sf.id
        self.sf = sf
        """ Parse RServer nodes and attach them to SF """
        if nodes != None:
            for node in nodes:
                rs = realserver.RealServer()
                rs.loadFromDict(node)
                rs.sf_id = sf.id
                rs.name = rs.id
                self.rs.append(rs)
                self.sf._rservers.append(rs)
        
        probes = params.get("healthMonitor",  None)
        if probes != None:
            for pr in probes:
                prb = createProbe(pr['type'])
                prb.loadFromDict(pr)
                prb.sf_id = sf.id
                prb.name = prb.id
                self.probes.append(prb)
                self.sf._probes.append(prb)
                
        vips = params.get('virtualIps',  None)
        
        if vips != None:
            for vip in vips:
                vs = virtualserver.VirtualServer()
                vs.loadFromDict(vip)
                vs.proto = lb.transport
                vs.appProto = lb.protocol
                vs.sf_id = sf.id
                vs.lb_id = lb.id
                vs.name = vs.id
                self.vips.append(vs)
                
        #stiky = params.get("sessionPersistence",  None)
        
                
    def savetoDB(self):
        store = balancer.storage.storage.Storage()
        wr = store.getWriter()
        
        wr.writeLoadBalancer(self.lb)
        wr.writeServerFarm(self.sf)
        wr.writePredictor(self.sf._predictor)
        for rs in self.rs:
            wr.writeRServer(rs)
        
        for pr in self.probes:
            wr.writeProbe(pr)
            
        for vip in self.vips:
            wr.writeVirtualServer(vip)
            
    def loadFromDB(self, lb_id):
        store = balancer.storage.storage.Storage()
        rd = store.getReader()
        self.lb = rd.getLoadBalancerById(lb_id)
        self.sf = rd.getSFByLBid(lb_id)
        sf_id = self.sf.id
        self.rs = rd.getRServersBySFid(sf_id)
        self.probes = rd.getProbesBySFid(sf_id)
        self.vips = rd.getVIPsBySFid(sf_id)
        
    def removeFromDB(self):
        store = balancer.storage.storage.Storage()
        dl = store.getDeleter()
        lb_id = self.lb.id
        sf_id = self.sf.id
        dl.deleteLBbyID(lb_id)
        dl.deleteSFbyLBid(lb_id)
        dl.deletePredictorBySFid(sf_id)
        
        dl.deleteRSsBySFid(sf_id)
        dl.deleteProbesBySFid(sf_id)
        dl.deleteVSsBySFid(sf_id)

#    def deploy(self,  driver,  context):
#        #Step 1. Deploy server farm
#        if  driver.createServerFarm(context,  self.sf) != "OK":
#            raise exception.OpenstackException
#        
#        #Step 2. Create RServers and attach them to SF
#        
#        for rs in self.rs:
#            driver.createRServer(context,  rs)
#            driver.addRServerToSF(context,  self.sf,  rs)
#            
#        #Step 3. Create probes and attache them to SF
#        for pr in self.probes:
#            driver.createProbe(context,  pr)
#            driver.addProbeToSF(context,  self.sf,  pr)
#        #Step 4. Deploy vip
#        for vip in self.vips:
#            driver.createVIP(context,  vip,  self.sf)   
        
        
def makeCreateLBCommandChain(bal,  driver,  context):
    list = []
    list.append(CreateServerFarmCommand(driver, context,  bal.sf))
    for rs in bal.rs:
        list.append(CreateRServerCommand(driver,  context, rs))
        list.append(AddRServerToSFCommand(driver, context, bal.sf,  rs))
    
    for pr in bal.probes:
        list.append(CreateProbeCommand(driver,  context,  pr))
        list.append(AddProbeToSFCommand(driver,  context,  bal.sf,  pr))
    for vip in bal.vips:
        list.append(CreateVIPCommand(driver,  context,  vip,  bal.sf))
    return list

def makeDeleteLBCommandChain(bal,  driver,  context):
    list = []
    for vip in bal.vips:
        list.append(DeleteVIPCommand(driver,  context,  vip,  bal.sf))
    for pr in bal.probes:
        list.append(DeleteProbeFromSFCommand(driver,  context,  bal.sf,  pr))
        list.append(DeleteProbeCommand(driver,  context,  pr))
    for rs in bal.rs:
        list.append(DeleteRServerFromSFCommand(driver, context, bal.sf,  rs))      
        list.append(DeleteRServerCommand(driver,  context, rs))
          
    list.append(DeleteServerFarmCommand(driver, context,  bal.sf))
    return list

class Deployer(object):
    def __init__(self):
        self.commands = []
    
    def execute(self):
        for index in range(len(self.commands)):
            current_command = self.commands[index]
            try:
                current_command.execute()
            except:
                i = index
                logger.error("Got exception during deploy. Rolling back changes.")
                
                for k in range(index):
                    command = self.commands[index - k]
                    command.undo()
                raise exception.Error()
                
                
class Destructor(object):    
    def __init__(self):
        self.commands = []
    
    def execute(self):
        for index in self.commands:
            try:
                index.execute()
            except:
                raise exception.Error()

class CreateRServerCommand(object): 
    def __init__(self,  driver,  contex,  rs):
        self._driver = driver
        self._context = contex
        self._rs = rs
    
    def execute(self):
         self._driver.createRServer(self._context,  self._rs)
    
    def undo(self):
        self._driver.deleteRServer(self._context,  self._rs)

class DeleteRServerCommand(object):
    def __init__(self,  driver,  contex,  rs):
        self._driver = driver
        self._context = context
        self._rs = rs
    
    def execute(self):
         self._driver.deleteRServer(self._context,  self._rs)

        
class CreateServerFarmCommand(object):
    def __init__(self,  driver,  context,  sf):
        self._driver = driver
        self._context = context
        self._sf = sf
    
    def execute(self):
        self._driver.createServerFarm(self._context,  self._sf)
        
    def undo(self):
        self._driver.deleteServerFarm(self._context,  self._sf)
        
class DeleteServerFarmCommand(object):
    def __init__(self,  driver,  context,  sf):
        self._driver = driver
        self._context = context
        self._sf = sf
    
    def execute(self):
        self._driver.deleteServerFarm(self._context,  self._sf)
        
class AddRServerToSFCommand(object):
    def __init__(self,  driver,  context,  sf, rs):
        self._driver = driver
        self._context = context
        self._sf = sf      
        self._rs = rs
        
    def execute(self):
        self._driver.addRServerToSF(self._context,  self._sf,  self._rs)
    def undo(self):
        self._driver.deleteRServerFromSF(self._context,  self._sf,  self._rs)

class DeleteRServerFromSFCommand(object):
    def __init__(self,  driver,  context,  sf, rs):
        self._driver = driver
        self._context = context
        self._sf = sf      
        self._rs = rs
        
    def execute(self):
        self._driver.deleteRServerFromSF(self._context,  self._sf,  self._rs)
        
class CreateProbeCommand(object):
    def __init__(self,  driver,  context,  probe):
        self._driver = driver
        self._context = context
        self._probe = probe
    
    def execute(self):
        self._driver.createProbe(self._context, self._probe)
    def undo(self):
        self._driver.deleteProbe(self._context, self._probe)

class DeleteProbeCommand(object):
    def __init__(self,  driver,  context,  probe):
        self._driver = driver
        self._context = context
        self._probe = probe
    
    def execute(self):
        self._driver.deleteProbe(self._context, self._probe)

class AddProbeToSFCommand(object):
    def __init__(self,  driver,  context,  sf,  probe):
        self._driver = driver
        self._context = context
        self._probe = probe
        self._sf = sf
    
    def execute(self):
        self._driver.addProbeToSF(self._context,  self._sf,  self._probe)
    def undo(self):
        self._driver.deleteProbeFromSF(self._context,  self._sf,  self._probe)

class DeleteProbeFromSFCommand(object):
    def __init__(self,  driver,  context,  sf,  probe):
        self._driver = driver
        self._context = context
        self._probe = probe
        self._sf = sf
    
    def execute(self):
        self._driver.deleteProbeFromSF(self._context,  self._sf,  self._probe)
        

class CreateVIPCommand(object):
    def __init__(self,  driver,  context,  vip,  sf):
        self._driver = driver
        self._context = context
        self._vip = vip
        self._sf = sf       
        
    def execute(self):
        self._driver.createVIP(self._context,  self._vip,  self._sf)
    def undo(self):
        self._driver.deleteVIP(self._context,  self._vip,  self._sf)

class DeleteVIPCommand(object):
    def __init__(self,  driver,  context,  vip,  sf):
        self._driver = driver
        self._context = context
        self._vip = vip
        self._sf = sf       

    def execute(self):
        self._driver.deleteVIP(self._context,  self._vip,  self._sf)    

def createProbe(probe_type):
    probeDict={'DNS':probe.DNSprobe(), 'ECHOTCP':probe.ECHOTCPprobe(), 'ECHOUDP':probe.ECHOUDPprobe(), 
        'FINGER':probe.FINGERprobe(), 'FTP':probe.FTPprobe(), 'HTTPS':probe.HTTPSprobe(), 'HTTP':probe.HTTPprobe(), 'ICMP':probe.ICMPprobe(), 
        'IMAP':probe.IMAPprobe(), 'POP':probe.POPprobe(), 'RADIUS':probe.RADIUSprobe(), 'RTSP':probe.RTSPprobe(), 'SCRIPTED':probe.SCRIPTEDprobe(), 
        'SIPTCP':probe.SIPTCPprobe(), 'SIPUDP':probe.SIPUDPprobe(), 'SMTP':probe.SMTPprobe(), 'SNMP':probe.SNMPprobe(), 
        'CONNECT':probe.TCPprobe(), 'TELNET':probe.TELNETprobe(), 'UDP':probe.UDPprobe(), 'VM':probe.VMprobe()}
    obj = probeDict.get(probe_type,  None)
    if obj == None:
        raise exception.NotFound("Can't create health monitoring probe of type %s" % probe_type)
    return obj.createSame()
    
def createPredictor(pr_type):
    predictDict={'HashAddr':predictor.HashAddrPredictor(), 'HashContent':predictor.HashContent(), 'HashCookie':predictor.HashCookie(), 'HashHeader':predictor.HashHeader(),
            'HashLayer4':predictor.HashLayer4(), 'HashURL':predictor.HashURL(), 'LeastBandwidth':predictor.LeastBandwidth(), 'LeastConn':predictor.LeastConn(), 
            'LeastLoaded':predictor.LeastLoaded(), 'Response':predictor.Response(), 'ROUND_ROBIN':predictor.RoundRobin()}
    
    obj = predictDict.get(pr_type,  None)
    if obj == None:
        raise exception.Invalid("Can't find load balancing algorithm with type %s" % pr_type)
    return obj.createSame()
    
