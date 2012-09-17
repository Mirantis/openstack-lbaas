import logging
import paramiko


LOG = logging.getLogger(__name__)


class RemoteControl(object):
    def __init__(self, device_ref):
        self.host = device_ref['ip']
        self.user = device_ref['user']
        self.password = device_ref['password']
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#        self.ssh.connect(self.host, username=self.user,
#                         password=self.password)
#
#    def __del__(self):
#        self.ssh.close()

    def perform(self, command):
        LOG.debug('performing command: {0}'.format(command))
        self.ssh.connect(self.host, username=self.user, password=self.password)
        stdout, stderr = self.ssh.exec_command(command)[1:]
        status = stdout.channel.recv_exit_status()
        out = stdout.read()
        err = stderr.read()
        LOG.debug('command exit status: {0}, stdout: {1}, stderr: {2}'
                  .format(status, out, err))

        self.ssh.close()
        return status, out

    def get_file(self, remote_path, local_path):
        LOG.debug('Copying remote file {0} to local {1}'.format(remote_path,
                                                                local_path))
        self.ssh.connect(self.host, username=self.user, password=self.password)
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        self.ssh.close()
        return True

    def put_file(self, local_path, remote_path):
        LOG.debug('Copying local file {0} to remote {1}'.format(local_path,
                                                                remote_path))
        self.ssh.connect(self.host, username=self.user, password=self.password)
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        self.ssh.close()
        return True


class RemoteService(RemoteControl):
    '''
    Operations with haproxy daemon
    '''

    def start(self):
        LOG.debug('Starting service haproxy')
        return self.perform('sudo service haproxy start')[0] == 0

    def stop(self):
        LOG.debug('Stopping service haproxy')
        return self.perform('sudo service haproxy stop')[0] == 0

    def restart(self):
        LOG.debug('Restarting haproxy')
        status = self.perform('sudo haproxy'
                              ' -f /etc/haproxy/haproxy.cfg'
                              ' -p /var/run/haproxy.pid'
                              ' -sf $(cat /var/run/haproxy.pid)')[0]

        return status == 0


class RemoteInterface(RemoteControl):
    def __init__(self, device_ref):
        super(RemoteInterface, self).__init__(device_ref)
        device_extra = device_ref.get('extra') or {}
        self.interface = device_extra.get('interface') or 'eth0'

    def add_ip(self, frontend):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        self.IP = frontend.bind_address
        LOG.debug('Trying to add IP-%s to inteface %s' %
                  (self.IP,  self.interface))
        stdout = self.ssh.exec_command('ip addr show dev %s' %
                                       self.interface)[1]
        ssh_out = stdout.read()
        if ssh_out.find(self.IP) < 0:
            self.ssh.exec_command('sudo ip addr add %s/32 dev %s' %
                                                (self.IP, self.interface))
            LOG.debug('Added ip %s to inteface %s' %
                      (self.IP, self.interface))
        else:
            LOG.debug('Remote ip %s is already configured on the %s' %
                      (self.IP, self.interface))
        self.ssh.close()
        return True

    def del_ip(self, frontend):
        self.ssh.connect(self.host, username=self.user, password=self.password)
        self.IP = frontend.bind_address
        stdin, stdout, stderr = self.ssh.exec_command('ip addr show dev %s' %
                               (self.interface))
        ssh_out = stdout.read()
        if  ssh_out.find(self.IP) >= 0:
            LOG.debug('Remote delete ip %s from inteface %s' %
                                    (self.IP, self.interface))
            self.ssh.exec_command('sudo ip addr del %s/32 dev %s' % (self.IP,
                                                   self.interface))
        else:
            LOG.debug('Remote ip %s is not configured on the %s' %
                                    (self.IP, self.interface))
        self.ssh.close()
        return True


class RemoteSocketOperation(RemoteControl):
    '''
    Remote operations via haproxy socket
    '''
    def __init__(self, device_ref):
        super(RemoteSocketOperation, self).__init__(device_ref)
        device_extra = device_ref.get('extra') or {}
        self.interface = device_extra.get('interface') or 'eth0'
        self.haproxy_socket = device_extra.get('socket') or '/tmp/haproxy.sock'
        self.backend_name = ''
        self.rserver_name = ''

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
        LOG.debug('Disable server %s/%s. Result is "%s"' %
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
        LOG.debug('Get statistics about reserver %s/%s.'
                    ' Result is \'%s\' ', backend, ssh_out)
        self.ssh.close()
        return ssh_out
