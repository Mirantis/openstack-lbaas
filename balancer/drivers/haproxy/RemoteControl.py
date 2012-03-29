import logging

from fabric.api import env, sudo, get, put, run
from fabric.network import disconnect_all

from balancer.drivers.haproxy.Context import Context

logger = logging.getLogger(__name__)

class RemoteConfig(object):
    def __init__(self, context):
        env.user = context.login
        env.hosts = []
        env.hosts.append(context.ip)
        env.password = context.password
        env.host_string = context.ip
        self.localpath = context.localpath
        self.remotepath = context.remotepath
        self.configfilename = context.configfilename

    def getConfig(self):
        get('%s/%s' % (self.remotepath,  self.configfilename), '%s/%s' % (self.localpath,  self.configfilename))
        disconnect_all()

    def putConfig(self):
        put(self.localpath+self.configfilename, '/tmp/'+self.configfilename)
        config_check_status = run('haproxy -c -f  /tmp/%s' % self.configfilename)
        if ( config_check_status  == 'Configuration file is valid'):
            sudo('mv /tmp/'+self.configfilename + " "+ self.remotepath)
            sudo('service haproxy restart')
            disconnect_all()
            return True
        else:
            logger.error('[HAPROXY] new config has errors')
            logger.debug(config_check_status)
            disconnect_all()
            return False
      

    def validationConfig(self): 
        env.warn_only = True
        return (run('haproxy -c -f  %s/%s' % (self.remotepath,  self.configfilename)) == 'Configuration file is valid')

class RemoteService(object):
    def __init__(self, context):
        env.user = context.login
        env.hosts = []
        env.hosts.append(context.ip)
        env.password = context.password
        env.host_string = context.ip
    
    def start(self):
        sudo('service haproxy start')
        disconnect_all()

    def stop(self):
        sudo('service haproxy stop')
        disconnect_all()
        
    def restart(self):
        sudo('service haproxy restart')
        disconnect_all()

class RemoteInterface(object):
    def __init__(self, context,  frontend):
        env.user = context.login
        env.hosts = []
        env.hosts.append(context.ip)
        env.password = context.password
        env.host_string = context.ip
        self.interface = context.interface
        self.IP = frontend.bind_address
        
    def changeIP(self, IP, netmask):
        sudo('ifconfig '+self.interface+ ' '+IP+' netmask '+netmask)
        disconnect_all()    
        
    def addIP(self):
        logger.debug('[HAPROXY] remote add ip %s to inteface %s' % (self.IP,  self.interface))        
        sudo('/sbin/ip addr add %s/32 dev %s'% (self.IP,  self.interface))
        disconnect_all()
        
    def delIP(self):
        logger.debug('[HAPROXY] remote delete ip %s from inteface %s' % (self.IP,  self.interface))
        sudo('/sbin/ip addr del %s/32 dev %s'% (self.IP,  self.interface))
        disconnect_all()
