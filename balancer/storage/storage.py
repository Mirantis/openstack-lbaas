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

class Reader(object):
    """ Reader class is used for db read opreations"""
    def __init__(self,  db):
        self._con = sqlite3.connect(db)
    
    def getLoadBalancers(self):
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM loadbalancers')
        rows = cur.fetchall()
        list = []
        for row in rows:
            lb = LoadBalancer()
            lb.loadFromRow(row)
            list.append(lb)
        return list
    
    def getLoadBalancerById(self,  id):
         cursor = self._con.cursor()
         cursor.execute('SELECT * FROM loadbalancers WHERE id = %s' % id)
         rows = cursor.fetchone()
         lb = LoadBalancer()
         lb.loadFromRow(rows)
         return lb
        

class Writer(object):
    def __init__(self,  db):
        self._con = sqlite3.connect(db)
    
    def writeLoadBalancer(self,  lb):
         cursor = self._con.cursor()
         command = "INSERT INTO loadbalancers (id, name, algorithm , status , created , updated ) VALUES(%d,'%s','%s','%s','%s','%s')" % (lb.id,  lb.name,  lb.algorithm,  lb.status,  lb.created,  lb.updated)
         cursor.execute(command)
       
        
class Storage(object):
    def __init__(self,  conf):
         self._db = conf['db_path']
         self._writer = Writer(self._db)

    def getReader(self):
        return Reader(self._db)
        
    def getWriter(self):
        return self._writer
        



