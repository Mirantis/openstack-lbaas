import sys
sys.path.append('balancer')
sys.path.append('balancer/drivers')
sys.path.append('balancer/drivers/cisco_ace')
sys.path.append('balancer/loadbalancers')



from AceDriver import AceDriver
from Context import Context
from realserver import RealServer



rs = RealServer()
rs.name = 'Test_to_delete'
rs.IP = '10.1.1.1'

cont = Context('10.4.15.30', '10443', 'admin', 'cisco123')
driver = AceDriver()
print driver.createRServer(cont, rs)
