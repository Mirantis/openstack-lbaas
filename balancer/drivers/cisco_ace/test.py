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




import sys
sys.path.append('balancer')
sys.path.append('balancer/drivers')
sys.path.append('balancer/drivers/cisco_ace')
sys.path.append('balancer/loadbalancers')

from AceDriver import AceDriver
from Context import Context
from realserver import RealServer
from serverfarm import ServerFarm
from probe import Probe

rs = RealServer()
rs.name = 'abc_RS_Host2'
rs.IP = '10.1.1.1'
rs.port = "8081"
rs.state = "inservice"
rs.minCon = None
rs.maxCon = None

sf = ServerFarm()
sf.name = "openstack_sfarm"
sf.predictor = "roundrobin"
sf.description = "description"

probe = Probe()
probe.name = "HTTP"

test_context = Context('10.4.15.30', '10443', 'admin', 'cisco123')
driver = AceDriver()

s = "  Creation The Real Server ...................... "
if (driver.createRServer(test_context, rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Deletion The Real Server ...................... "
if (driver.deleteRServer(test_context, rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Activation The Real Server .................... "
if (driver.activateRServer(test_context, sf, rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Suspend The Real Server ....................... "
if (driver.suspendRServer(test_context, sf, rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Creation The Server Farm ...................... "
if (driver.createServerFarm(test_context, sf) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Add Probe To Server Farm ...................... "
if (driver.addProbeToSF(test_context, sf,  probe) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Remove Probe From Server Farm ................. "
if (driver.deleteProbeFromSF(test_context, sf,  probe) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Add RServer To Server Farm .................... "
if (driver.addRServerToSF(test_context, sf,  rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

s = "  Delete RServer To Server Farm ................. "
if (driver.deleteRServerFromSF(test_context, sf,  rs) == 'OK'):
    print s + '\x1b[32m OK \x1b[0m'
else:
    print s + '\x1b[31m ERROR \x1b[0m'

print "The Test is Complite."
