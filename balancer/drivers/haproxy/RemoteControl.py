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
        logger.debug('[HAPROXY] get configuration to remote server')
        get('%s/%s' % (self.remotepath,  self.configfilename), '%s/%s' % \
                                   (self.localpath,  self.configfilename))
        disconnect_all()

    def putConfig(self):
        logger.debug('[HAPROXY] put configuration to remote server')
        put(self.localpath + self.configfilename, '/tmp/' + \
                                         self.configfilename)
        #config_check_status = run('haproxy -c -f  /tmp/%s' % \
        #                                  self.configfilename)
        sudo('mv /tmp/' + self.configfilename + " " + self.remotepath)
        #sudo('service haproxy restart')
#        if ( config_check_status  == 'Configuration file is valid'):
#            sudo('mv /tmp/' + self.configfilename + " "+ self.remotepath)
#            sudo('service haproxy restart')
#            disconnect_all()
#            return True
#        else:
#            logger.error('[HAPROXY] new config has errors')
#            logger.debug(config_check_status)
#            disconnect_all()
#            return False

    def validationConfig(self):
        '''
            Validate conifig and restart haproxy
        '''
        env.warn_only = True
        if run('haproxy -c -f  %s/%s' % (self.remotepath,  \
                self.configfilename)).find('Configuration file is valid') >= 0:
            logger.debug('[HAPROXY] remote configuration is valid, \
                                                              restart haproxy')
            sudo('service haproxy restart')
            return True
        else:
            logger.error('[HAPROXY] remote configuration is not valid')
            return False


class RemoteService(object):
    '''
    Operations with haproxy daemon
    '''
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
        sudo('ifconfig ' + self.interface + ' ' + IP + ' netmask ' + netmask)
        disconnect_all()

    def addIP(self):
        if run('/sbin/ip addr show dev %s' % self.interface).find(self.IP) < 0:
            sudo('/sbin/ip addr add %s/32 dev %s' % (self.IP,  self.interface))
            logger.debug('[HAPROXY] remote add ip %s to inteface %s' % \
                                              (self.IP,  self.interface))
        else:
            logger.debug('[HAPROXY] remote ip %s is already configured on the \
                                              %s' % (self.IP,  self.interface))
        disconnect_all()

    def delIP(self):
        if run('/sbin/ip addr show dev %s' % \
               self.interface).find(self.IP) >= 0:
            logger.debug('[HAPROXY] remote delete ip %s from inteface %s' % \
                                                  (self.IP,  self.interface))
            sudo('/sbin/ip addr del %s/32 dev %s' % (self.IP,  self.interface))
        else:
            logger.debug('[HAPROXY] remote ip %s is not configured on the %s' \
                                                  % (self.IP,  self.interface))
        disconnect_all()


class RemoteSocketOperation(object):
    '''
    Remote operations via haproxy socket
    '''
    def __init__(self, context,  backend,  rserver):
        env.user = context.login
        env.hosts = []
        env.hosts.append(context.ip)
        env.password = context.password
        env.host_string = context.ip
        self.interface = context.interface
        self.haproxy_socket = context.haproxy_socket
        self.backend_name = backend.name
        self.rserver_name = rserver.name

    def  suspendServer(self):
        out = sudo('echo disable server %s/%s | socat stdio unix-connect:%s' %\
                  (self.backend_name, self.rserver_name,  self.haproxy_socket))
        if out == "":
            out = 'ok'
        logger.debug('[HAPROXY] disable server  %s/%s. Result is "%s"' %\
                      (self.backend_name,  self.rserver_name,  out))
        disconnect_all()

    def activateServer(self):
        out = sudo('echo enable server %s/%s | socat stdio unix-connect:%s' % \
                  (self.backend_name, self.rserver_name,  self.haproxy_socket))
        if out == "":
            out = 'ok'
        logger.debug('[HAPROXY] enable server  %s/%s. Result is "%s"' % \
                      (self.backend_name,  self.rserver_name,  out))
        disconnect_all()
    
    def getRserverStatistics(self):
        out = sudo ('echo show stat | socat stdio unix-connect:%s | grep %s,%s ' % \
                  (self.haproxy_socket,  self.backend_name, self.rserver_name ))
        logger.debug ('[HAPROXY] get statistics about reserver %s/%s. Result is '  % \
                      (self.backend_name,  self.rserver_name,  out))
        disconnect_all()
    
    def getBackendStatistics(self):
        out = sudo ('echo show stat | socat stdio unix-connect:%s | grep %s,BACKEND ' % \
                  (self.haproxy_socket,  self.backend_name, self.rserver_name ))
        logger.debug ('[HAPROXY] get statistics about backend %s. Result is '  % \
                      (self.backend_name,  out))       
        disconnect_all()
