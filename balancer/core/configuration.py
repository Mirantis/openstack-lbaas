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


import logging
import sys
import threading

from balancer.common.utils import *
logger = logging.getLogger(__name__)

@Singleton
class Configuration(object):
    def __init__(self):
        self._config = None
        self._lock = threading.Lock()
    
    def put(self,  conf):
        msg = "Put config: %s" % conf
        logger.debug(msg)
        self._lock.acquire()
        self._config = conf
        self._lock.release()
    
    def get(self):
        self._lock.acquire()
        conf = self._config
        self._lock.release()
        return conf
        
        
