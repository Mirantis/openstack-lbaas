# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
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

import sqlite3

from balancer.loadbalancers.loadbalancer import *
from openstack.common import exception
from balancer.devices.device import LBDevice
from balancer.core.configuration import Configuration
logger = logging.getLogger(__name__)


class Reader(object):
    """ Reader class is used for db read opreations"""
    def __init__(self,  db):
        logger.debug("Reader: connecting to db: %s" % db)
        self._con = sqlite3.connect(db)
        self._probeDict={'DNSprobe':probe.DNSprobe(), 'ECHOTCPprobe':probe.ECHOTCPprobe(), 'ECHOUDPprobe':probe.ECHOUDPprobe(), 
        'FINGERprobe':probe.FINGERprobe(), 'FTPprobe':probe.FTPprobe(), 'HTTPSprobe':probe.HTTPSprobe(), 'HTTPprobe':probe.HTTPprobe(), 'ICMPprobe':probe.ICMPprobe(), 
        'IMAPprobe':probe.IMAPprobe(), 'POPprobe':probe.POPprobe(), 'RADIUSprobe':probe.RADIUSprobe(), 'RTSPprobe':probe.RTSPprobe(), 'SCRIPTEDprobe':probe.SCRIPTEDprobe(), 
        'SIPTCPprobe':probe.SIPTCPprobe(), 'SIPUDPprobe':probe.SIPUDPprobe(), 'SMTPprobe':probe.SMTPprobe(), 'SNMPprobe':probe.SNMPprobe(), 
        'TCPprobe':probe.TCPprobe(), 'TELNETprobe':probe.TELNETprobe(), 'UDPprobe':probe.UDPprobe(), 'VMprobe':probe.VMprobe()}
    
    def getLoadBalancers(self):
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM loadbalancers')
        rows = cursor.fetchall()
        if rows == None:
             raise exception.NotFound()
        list = []
        for row in rows:
            lb = LoadBalancer()
            lb.loadFromRow(row)
            list.append(lb)
        return list
    
    def getLoadBalancerById(self,  id):
         cursor = self._con.cursor()
         cursor.execute('SELECT * FROM loadbalancers WHERE id = %s' % id)
         row = cursor.fetchone()
         if row == None:
             raise exception.NotFound()
         lb = LoadBalancer()
         lb.loadFromRow(row)
         return lb
    
    def getDeviceById(self,  id):
         cursor = self._con.cursor()
         if id == None:
             raise exception.NotFound("Empty device id.")
         cursor.execute('SELECT * FROM devices WHERE id = %s' % id)
         row = cursor.fetchone()
         if row == None:
             raise exception.NotFound()
         lb = LBDevice()
         lb.loadFromRow(row)
         return lb

    def getDevices(self):
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM devices')
        rows = cursor.fetchall()
        if rows == None:
             raise exception.NotFound()
        list = []
        for row in rows:
            lb = LBDevice()
            lb.loadFromRow(row)
            list.append(lb)
        return list

    def getProbeById(self, id):
        self._con.row_factory = sqlite3.Row
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM probes WHERE id = %s' % id)
        row = cursor.fetchone()
        if row == None:
            raise exception.NotFound()
        prb = self._probeDict[row[0]]
        prb.loadFromRow(row)
        return prb     

    def getProbes(self):
        self._con.row_factory = sqlite3.Row
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM probes')
        rows = cursor.fetchall()
        if rows == None:
             raise exception.NotFound()
        list = []
        for row in rows:
            prb = self._probeDict[row[0]]
            prb.loadFromRow(row)
            list.append(prb)
        return list        

class Writer(object):
    def __init__(self,  db):
        logger.debug("Writer: connecting to db: %s" % db)
        self._con = sqlite3.connect(db)
    
    def writeLoadBalancer(self,  lb):
         logger.debug("Saving LoadBalancer instance in DB.")
         cursor = self._con.cursor()
         command = "INSERT INTO loadbalancers (id, name, algorithm , status , created , updated ) VALUES(%d,'%s','%s','%s','%s','%s');"  % (lb.id,  lb.name,  lb.algorithm,  lb.status,  lb.created,  lb.updated)
         msg = "Executing command: %s" % command
         logger.debug(msg)
         cursor.execute(command)
         self._con.commit()
         
    def writeDevice(self,  device):
         logger.debug("Saving Device instance in DB.")
         cursor = self._con.cursor()
         command = "INSERT INTO devices (id,  name, type, version, supports_IPv6, require_VIP_IP, has_ACL, supports_VLAN, ip, port, user, pass ) VALUES('%s','%s','%s','%s',%d, %d, %d, %d,'%s','%s','%s','%s');"  % (device.id,  device.name,  
                                                                                                                                                                                                device.type,  device.version,  device.supports_IPv6,  device.require_VIP_IP, device.has_ACL,  device.supports_VLAN,  
                                                                                                                                                                                                device.ip,  device.port,  device.user,  device.password )
         msg = "Executing command: %s" % command
         logger.debug(msg)
         cursor.execute(command)
         self._con.commit()
        
    def writeProbe(self, prb):
        logger.debug("Saving Probe instance in DB.")
        cursor = self._con.cursor()
        dict = prb.convertToDict()
        command = "INSERT INTO probes ("
        i=0
        for key in dict.keys():
            if i < len(dict)-1:
                command = command + key+','
            else:
                command = command + key
            i+=1
        command += ") VALUES("
        i=0
        for val in dict.values():
            if i < len(dict)-1:
                command +=str(val) + ","
            else:
                command +=str(val) + ");"
            i+=1
        msg = "Executing command: %s" % command
        logger.debug(msg)
        cursor.execute(command)
        self._con.commit()            
         
        
       
        
class Storage(object):
    def __init__(self,  conf=None):
         if conf == None:
            conf_data = Configuration.Instance()
            conf = conf_data.get()
            db = conf['db_path']
         self._db =db
         self._writer = Writer(self._db)

    def getReader(self):
        return Reader(self._db)
        
    def getWriter(self):
        return self._writer
        



