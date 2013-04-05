import logging
import paramiko

from balancer.common import cfg

LOG = logging.getLogger(__name__)

key_opt = cfg.StrOpt('haproxy_ssh_key_path')


class RemoteControl(object):
    def __init__(self, conf, device_ref):
        self.host = device_ref['ip']
        self.user = device_ref['user']
        if 'password' in device_ref:
            LOG.warn('Using SSH password to access HAproxy device %s',
                     device_ref['id'])
            self.password = device_ref['password']
        else:
            self.password = None
            try:
                self.key = conf.haproxy_ssh_key_path
            except cfg.NoSuchOptError:
                conf.register_opt(key_opt)
                self.key = conf.haproxy_ssh_key_path
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.closed = True

    def open(self):
        if self.closed:
            if self.password is not None:
                self._ssh.connect(self.host, username=self.user,
                                  password=self.password)
            else:
                self._ssh.connect(self.host, username=self.user,
                                  key_filename=self.key)
            self.closed = False

    def close(self):
        if not self.closed:
            self._ssh.close()
            self.closed = True

    def perform(self, command):
        self.open()
        LOG.debug('performing command: {0}'.format(command))
        stdout, stderr = self._ssh.exec_command(command)[1:]
        status = stdout.channel.recv_exit_status()
        out = stdout.read()
        err = stderr.read()
        LOG.debug('command exit status: {0}, stdout: {1}, stderr: {2}'
                  .format(status, out, err))

        return status, out, err

    def get_file(self, remote_path, local_path):
        self.open()
        LOG.debug('Copying remote file {0} to local {1}'.format(remote_path,
                                                                local_path))
        sftp = self._ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return True

    def put_file(self, local_path, remote_path):
        self.open()

        LOG.debug('Copying local file {0} to remote {1}'.format(local_path,
                                                                remote_path))
        sftp = self._ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True


class RemoteService(object):
    '''
    Operations with haproxy daemon
    '''
    def __init__(self, remote_ctrl):
        self.remote_ctrl = remote_ctrl

    def start(self):
        LOG.debug('Starting service haproxy')
        return self.remote_ctrl.perform('sudo service haproxy start')[0] == 0

    def stop(self):
        LOG.debug('Stopping service haproxy')
        return self.remote_ctrl.perform('sudo service haproxy stop')[0] == 0

    def restart(self):
        LOG.debug('Restarting haproxy')
        status = self.remote_ctrl.perform('sudo haproxy'
                              ' -f /etc/haproxy/haproxy.cfg'
                              ' -p /var/run/haproxy.pid'
                              ' -sf $(cat /var/run/haproxy.pid)')[0]

        return status == 0


class RemoteInterface(object):
    def __init__(self, device_ref, remote_ctrl):
        device_extra = device_ref.get('extra') or {}
        self.interface = device_extra.get('interface') or 'eth0'
        self.remote_ctrl = remote_ctrl

    def add_ip(self, frontend):
        self.IP = frontend.bind_address
        LOG.debug('Trying to add IP-%s to inteface %s' %
                  (self.IP,  self.interface))
        ssh_out = self.remote_ctrl.perform('ip addr show dev %s' %
                                           self.interface)[1]
        if ssh_out.find(self.IP) < 0:
            self.remote_ctrl.perform('sudo ip addr add %s/32 dev %s' %
                                     (self.IP, self.interface))
            LOG.debug('Added ip %s to inteface %s' %
                      (self.IP, self.interface))
        else:
            LOG.debug('Remote ip %s is already configured on the %s' %
                      (self.IP, self.interface))
        return True

    def del_ip(self, frontend):
        self.IP = frontend.bind_address
        ssh_out = self.remote_ctrl.perform('ip addr show dev %s' %
                                           (self.interface))[1]
        if  ssh_out.find(self.IP) >= 0:
            LOG.debug('Remote delete ip %s from inteface %s' %
                                    (self.IP, self.interface))
            self.remote_ctrl.perform('sudo ip addr del %s/32 dev %s' %
                                     (self.IP, self.interface))
        else:
            LOG.debug('Remote ip %s is not configured on the %s' %
                                    (self.IP, self.interface))
        return True


class RemoteSocketOperation(object):
    '''
    Remote operations via haproxy socket
    '''
    def __init__(self, device_ref, remote_ctrl):
        device_extra = device_ref.get('extra') or {}
        self.interface = device_extra.get('interface') or 'eth0'
        self.haproxy_socket = device_extra.get('socket') or '/tmp/haproxy.sock'
        self.remote_ctrl = remote_ctrl

    def suspend_server(self, backend, rserver):
        self._operation_with_server_via_socket('disable', backend.name,
                                               rserver['id'])
        return True

    def activate_server(self, backend, rserver):
        self._operation_with_server_via_socket('enable', backend.name,
                                                rserver['id'])
        return True

    def _operation_with_server_via_socket(self, operation, backend_name,
                                          server_name):
        ssh_out = self.remote_ctrl.perform(
                'echo %s server %s/%s | sudo socat stdio unix-connect:%s' %
                (operation,  backend_name,
                 server_name, self.haproxy_socket))[1]
        if  ssh_out == "":
            out = 'ok'
        else:
            out = 'is not ok'
        LOG.debug('Disable server %s/%s. Result is "%s"' %
                      (backend_name, server_name, out))

    def get_statistics(self, backend_name, server_name):
        """
            Get statistics from rserver / server farm
            for all server farms use BACKEND as self.rserver_name
        """
        ssh_out = self.remote_ctrl.perform(
           'echo show stat | sudo socat stdio unix-connect:%s | grep %s,%s' %
            (self.haproxy_socket, backend_name, server_name))[1]
        LOG.debug('Get statistics about reserver %s/%s.'
                    ' Result is \'%s\' ', backend_name, ssh_out)
        return ssh_out
