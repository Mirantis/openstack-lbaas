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
import logging
import openstack.common.exception

logger = logging.getLogger(__name__)


class XmlSender:
    def __init__(self, device_ref):
        #port 10443
        self.url = "https://%s:%s/bin/xml_agent" % (device_ref.ip,
                                                    device_ref.port)
        base64str = base64.encodestring('%s:%s' % \
            (device_ref.login, device_ref.password))[:-1]

        self.authheader = "Basic %s" % base64str

    def getParam(self, name):
        return self._params.get(name, None)

    def deployConfig(self, command):
        request = urllib2.Request(self.url)
        request.add_header("Authorization", self.authheader)

        d = """xml_cmd=<request_raw>\nconfigure\n%s\nend\n</request_raw>""" \
            % command
        logger.debug("send data to ACE:\n" + d)

        try:
            message = urllib2.urlopen(request, d)
            s = message.read()
        except (Exception):
            raise openstack.common.exception.Error(Exception)

        logger.debug("data from ACE:\n" + s)

        if (s.find('XML_CMD_SUCCESS') > 0):
            return 'OK'
        else:
            raise openstack.common.exception.Invalid(s)

    def getConfig(self, command):
        request = urllib2.Request(self.url)
        request.add_header("Authorization", self.authheader)

        data = """xml_cmd=<request_raw>\nshow runn %s\n</request_raw>""" \
               % command
        logger.debug("send data to ACE:\n" + data)

        try:
            message = urllib2.urlopen(request, data)
            s = message.read()
        except (Exception):
            raise openstack.common.exception.Error(Exception)

        logger.debug("data from ACE:\n" + s)

        return s
