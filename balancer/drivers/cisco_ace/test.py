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
rs.name = 'abc_RS_Host'
rs.IP = '10.1.1.1'
rs.port = "10"
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
print "||===  Creation The Real Server  ============||"
#print driver.createRServer(test_context, rs)
print "||===  Deletion The Real Server  ============||"
#print driver.deleteRServer(test_context, rs)
print "||===  Activation The Real Server  ==========||"
#print driver.activateRServer(test_context, sf, rs)
print "||===  Suspend The Real Server  =============||"
#print driver.suspendRServer(test_context, sf, rs)
print "||===  Creation The Server Farm  ============||"
#print driver.createServerFarm(test_context, sf)
print "||===  Add Probe To Server Farm  ============||"
#print driver.addProbeToSF(test_context, sf,  probe)
print "||===  Remove Probe From Server Farm  =======||"
#print driver.removeProbeFromSF(test_context, sf,  probe)
print "||===  Add RServer To Server Farm  ==========||"
#print driver.addRServerToSF(test_context, sf,  rs)
print "||===  Delete RServer To Server Farm  =======||"
print driver.deleteRServerFromSF(test_context, sf,  rs)
print "||=============  Test Complite  =============||"
