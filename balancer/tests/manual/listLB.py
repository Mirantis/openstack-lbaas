
from fabric.colors import  green
from fabric.colors import  yellow
from fabric.colors import  red
from balancer.client import V1Client

def colorize(status):
    if status.lower() == 'error':
        return red(status)
    if status.lower() == 'build':
        return yellow(status)
    if status.lower() == 'active':
        return green(status)
    return status
        
    
client = V1Client("127.0.0.1",  8181)
lbs = client.get_loadbalancers()
for lb in lbs:
    str = '| %s | %s |' % (lb['name'],   colorize(lb['status']))
    print str
print '------------------------------------------------'
