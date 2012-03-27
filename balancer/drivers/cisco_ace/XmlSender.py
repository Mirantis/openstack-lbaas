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


import urllib2
import base64
import re 
import logging
from balancer.drivers.cisco_ace.Context import Context
import openstack.common.exception

logger = logging.getLogger(__name__)

class XmlSender:
    def __init__(self,  context):
        self.url = "https://%s:10443/bin/xml_agent" % (context.ip)

    def getParam(self, name):
        return self._params.get(name,  None)
    
    def deployConfig(self,  context,  command):
        request = urllib2.Request(self.url)
        
        base64str = base64.encodestring('%s:%s' % (context.login, context.password))[:-1]
        
        authheader = "Basic %s" % base64str
        
        request.add_header("Authorization", authheader)
        
        data = """xml_cmd=<request_xml>\r\n%s\r\n</request_xml>""" % command
        
        logger.debug("send data to ACE:\n" + data)
        
        try:
            message = urllib2.urlopen(request, data)
            s = message.read()
            
            logger.debug("data from ACE:\n" + s)
            
            if (s.find('XML_CMD_SUCCESS') > 0):
                return 'OK'
            else:
                raise openstack.common.exception.Invalid(s)
                
        except:
            logger.debug("\n Device error \n")
            return 'DEVICE ERROR'
