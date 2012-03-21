import sys
sys.path.append('balancer')
sys.path.append('balancer/drivers')
sys.path.append('balancer/drivers/cisco_ace')
sys.path.append('balancer/loadbalancers')

from AceDriver import AceDriver
from Context import Context
from realserver import RealServer
from serverfarm import ServerFarm

rs = RealServer()
rs.name = 'Test_to_delete'
rs.IP = '10.1.1.1'

sf = ServerFarm()
sf.name = "openstack_sfarm"
sf.predictor = "roundrobin"
sf.description = "description"

test_context = Context('10.4.15.30', '10443', 'admin', 'cisco123')
driver = AceDriver()
print "||===  Creation The Real Server  ============||"
#print driver.createRServer(test_context, rs)
print "||===  Deletion The Real Server  ============||"
#print driver.deleteRServer(test_context, rs)
print "||===  Creation The Server Farm  ============||"
print driver.createServerFarm(test_context, sf)
print "||=============  Test Complite  =============||"
