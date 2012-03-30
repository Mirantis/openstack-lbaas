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

from balancer.drivers.BaseDriver import BaseDriver
from balancer.drivers.BaseDriver import BaseContext


class Context(BaseContext):
    def __init__(self, ip = '', port='22', login='', password='', localpath='/tmp/', configfilename='haproxy.cfg', \
                 remotepath='/etc/haproxy/',  interface =''):
        self.ip = ip
        self.port = port
        if (localpath is None) or (localpath == "None"):
                self.localpath = '/tmp/'
        else:
                self.localpath = localpath
        
        self.login = login
        self.password = password
        
        if (remotepath is None) or (remotepath == "None"):
                self.remotepath = '/etc/haproxy/'
        else:
                self.remotepath = remotepath
        
        if (configfilename is None) or (configfilename == "None"):
                self.configfilename = 'haproxy.cfg'
        else:
                self.configfilename = configfilename

        if (interface is None) or (interface == "None"):
                self.interface = ''
        else:
                self.interface = interface

        
