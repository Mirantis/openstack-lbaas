import logging
import paramiko


logger = logging.getLogger(__name__)


class RemoteConfig(object):
    def __init__(self, device_ref, localpath, remotepath, configfilename):
        self.host = device_ref['ip']
        self.user = device_ref['user']
        self.password = device_ref['password']
        self.remotepath = remotepath
        self.configfilename = configfilename
        self.localpath = localpath
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def get_config(self):
        logger.debug('[HAPROXY] copying config from the '
                     'remote server %s/%s to %s/%s' %
                      (self.remotepath, self.configfilename,
                       self.localpath, self.configfilename))
        self.ssh.connect(self.host, username=self.user, password=self.password)
        sftp = self.ssh.open_sftp()
        sftp.get('%s/%s' % (self.remotepath, self.configfilename),
                 '%s/%s' % (self.localpath, self.configfilename))
        sftp.close()
        self.ssh.close()
        return True

    def put_config(self):
        logger.debug('[HAPROXY] copying configuration to the remote server')
        self.ssh.connect(self.host, username=self.user, password=self.password)
        sftp = self.ssh.open_sftp()
        sftp.put('%s/%s' % (self.localpath, self.configfilename),
                 '/tmp/%s.remote' % self.configfilename)
        self.ssh.exec_command('sudo mv /tmp/%s.remote %s/%s' %
                              (self.configfilename, self.remotepath,
                               self.configfilename))
        sftp.close()
        self.ssh.close()
        return True

    def validate_config(self):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        stdout = self.ssh.exec_command('haproxy -c -f %s/%s' %
                                       (self.remotepath,
                                        self.configfilename))[1]
        ssh_out = stdout.read()
        self.ssh.close()
        logger.debug('[HAPROXY] ssh_out - %s - %s' % (ssh_out,
                         ssh_out.find('Configuration file is valid')))
        if 'Configuration file is valid' in ssh_out:
            logger.debug('[HAPROXY] remote configuration is valid')
            return True
        else:
            logger.error('[HAPROXY] remote configuration is not valid')
            return False


class RemoteService(object):
    '''
    Operations with haproxy daemon
    '''
    def __init__(self, device_ref):
        self.host = device_ref['ip']
        self.user = device_ref['user']
        self.password = device_ref['password']
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def start(self):
        self.ssh.connect(self.host, username=self.user, password=self.password)

        logger.debug('[HAPROXY] starting service haproxy')
        stdout = self.ssh.exec_command('sudo service haproxy start')[1]
        status = stdout.channel.recv_exit_status()
        logger.debug('[HAPROXY] haproxy start result - {0}'.format(status))

        self.ssh.close()
        return status == 0

    def stop(self):
        self.ssh.connect(self.host, username=self.user, password=self.password)

        logger.debug('[HAPROXY] stopping service haproxy')
        stdout = self.ssh.exec_command('sudo service haproxy stop')[1]
        status = stdout.channel.recv_exit_status()
        logger.debug('[HAPROXY] haproxy stop result - {0}'.format(status))

        self.ssh.close()
        return status == 0

    def restart(self):
        self.ssh.connect(self.host, username=self.user, password=self.password)

        logger.debug('[HAPROXY] restarting haproxy')
        stdout = self.ssh.exec_command('sudo haproxy'
                                       ' -f /etc/haproxy/haproxy.cfg'
                                       ' -p /var/run/haproxy.pid'
                                       ' -sf $(cat /var/run/haproxy.pid)')[1]
        status = stdout.channel.recv_exit_status()
        logger.debug('[HAPROXY] haproxy restart output: %s', stdout.read())
        logger.debug('[HAPROXY] haproxy restart returned - %s', status)

        self.ssh.close()
        return status == 0


class RemoteInterface(object):
    def __init__(self, device_ref):
        device_extra = device_ref.get('extra')
        self.interface = device_extra.get('interface')
        self.host = device_ref['ip']
        self.user = device_ref['user']
        self.password = device_ref['password']
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def add_ip(self, frontend):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        self.IP = frontend.bind_address
        logger.debug('[HAPROXY] trying to add IP-%s to inteface %s' %
                                (self.IP,  self.interface))
        stdin, stdout, stderr = self.ssh.exec_command('ip addr show dev %s' %
                                self.interface)
        ssh_out = stdout.read()
        if ssh_out.find(self.IP) < 0:
            self.ssh.exec_command('sudo ip addr add %s/32 dev %s' %
                                                (self.IP, self.interface))
            logger.debug('[HAPROXY] added ip %s to inteface %s' %
                                              (self.IP, self.interface))
        else:
            logger.debug('[HAPROXY] remote ip %s is already configured on the \
                                              %s' % (self.IP, self.interface))
        self.ssh.close()
        return True

    def del_ip(self, frontend):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        self.IP = frontend.bind_address
        stdin, stdout, stderr = self.ssh.exec_command('ip addr show dev %s' %
                               (self.interface))
        ssh_out = stdout.read()
        if  ssh_out.find(self.IP) >= 0:
            logger.debug('[HAPROXY] remote delete ip %s from inteface %s' %
                                    (self.IP, self.interface))
            self.ssh.exec_command('sudo ip addr del %s/32 dev %s' % (self.IP,
                                                   self.interface))
        else:
            logger.debug('[HAPROXY] remote ip %s is not configured on the %s' %
                                    (self.IP, self.interface))
        self.ssh.close()
        return True


class RemoteSocketOperation(object):
    '''
    Remote operations via haproxy socket
    '''
    def __init__(self, device_ref):
        device_extra = device_ref.get('extra')
        self.interface = device_extra.get('interface')
        self.haproxy_socket = device_extra.get('socket')
        self.host = device_ref['ip']
        self.user = device_ref['user']
        self.password = device_ref['password']
        self.backend_name = ''
        self.rserver_name = ''
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def suspend_server(self, backend, rserver):
        self.backend_name = backend.name
        self.rserver_name = rserver['id']
        self._operation_with_server_via_socket('disable')
        return True

    def activate_server(self, backend, rserver):
        self.backend_name = backend.name
        self.rserver_name = rserver['id']
        self._operation_with_server_via_socket('enable')
        return True

    def _operation_with_server_via_socket(self, operation):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        stdin, stdout, stderr = self.ssh.exec_command(
                'echo %s server %s/%s | sudo socat stdio unix-connect:%s' %
                (operation,  self.backend_name,
                 self.rserver_name, self.haproxy_socket))
        ssh_out = stdout.read()
        if  ssh_out == "":
            out = 'ok'
        else:
                out = 'is not ok'
        logger.debug('[HAPROXY] disable server %s/%s. Result is "%s"' %
                      (self.backend_name, self.rserver_name, out))
        self.ssh.close()

    def get_statistics(self, socket, backend):
        """
            Get statistics from rserver / server farm
            for all serverafarm use BACKEND as self.rserver_name
        """
        self.ssh.connect(self.host, username=self.user, password=self.password)
        stdin, stdout, stderr = self.ssh.exec_command(
           'echo show stat | sudo socat stdio unix-connect:%s | grep %s' %
            (socket, backend))
        ssh_out = stdout.read()
        logger.debug('[HAPROXY] get statistics about reserver %s/%s.'
                    ' Result is \'%s\' ', backend, ssh_out)
        self.ssh.close()
        return ssh_out
