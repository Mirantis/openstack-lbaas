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

logger = logging.getLogger(__name__)


class Reader(object):
    """ Reader class is used for db read opreations"""
    def __init__(self,  db):
        logger.debug("Reader: connecting to db: %s" % db)
        self._con = sqlite3.connect(db)
    
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

    def getDevices(self,):
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
         command = "INSERT INTO devices (id,  name, type, version, supports_IPv6, require_VIP_IP, has_ACL, supports_VLAN ) VALUES(%d,'%s','%s','%s',%d, %d, %d, %d);"  % (device.id,  device.name,  device.type,  device.version,  device.supports_IPv6,  device.require_VIP_IP, device.has_ACL,  device.supports_VLAN )
         msg = "Executing command: %s" % command
         logger.debug(msg)
         cursor.execute(command)
         self._con.commit()
        
        
         
        
       
        
class Storage(object):
    def __init__(self,  conf):
         self._db = conf['db_path']
         self._writer = Writer(self._db)

    def getReader(self):
        return Reader(self._db)
        
    def getWriter(self):
        return self._writer
        



