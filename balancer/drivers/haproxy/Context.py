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
    def __init__(self, ip = '', port='', login='', password='', localpath='', localname='', remotepath='', \
                  remotename ='', interface =''):
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.localpath = localpath
        self.remotepath = remotepath
        self.localname = localname
        self.remotename = remotename
        self.interface = interface

        
