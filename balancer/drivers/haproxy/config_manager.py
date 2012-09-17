import logging
import os.path

from remote_control import RemoteControl

LOG = logging.getLogger(__name__)


class ConfigManager(object):
    def __init__(self, device_ref):
        device_extra = device_ref.get('extra') or {}
        self.remote_config_path = (device_extra.get('remote_config_path') or
                            '/etc/haproxy/haproxy.cfg')
        self.local_config_path = '/tmp/haproxy.cfg'
        self.remote_control = RemoteControl(device_ref)
        self.config = {}
        self.need_deploy = False

    def __del__(self):
        if os.path.exists(self.local_config_path):
            os.remove(self.local_config_path)

    def deploy_config(self):
        if self.need_deploy:
            LOG.debug("Deploying configuration")
            tmp_path = '/tmp/haproxy.cfg.remote'
            self.remote_control.put_file(self.local_config_path,
                                         tmp_path)
            if self._validate_config(tmp_path):
                self.remote_control.perform('sudo mv {0} {1}'
                                            .format(tmp_path,
                                                    self.remote_config_path))
                self.need_deploy = False

            return not self.need_deploy
        else:
            return False

    def add_lines_to_block(self, block, lines):
        self._fetch_config()
        LOG.debug('Adding lines to {0} {1}: {2}'.format(block.type, block.name,
                                                        lines))
        for key in self.config:
            if block.type in key and block.name in key:
                self.config[key] += lines

        self._apply_config()

    def del_lines_from_block(self, block, lines):
        '''
            For every <del_line> in <lines> deletes the whole line from <block>
            if this line contains <del_line>
        '''
        self._fetch_config()
        LOG.debug('Deleting lines from {0} {1}: {2}'
                  .format(block.type, block.name, lines))
        for key in self.config:
            if block.type in key and block.name in key:
                for del_line in lines:
                    for line in self.config[key]:
                        if del_line in line:
                            self.config[key].remove(line)
        self._apply_config()

    def add_rserver(self, backend_name, server):
        if not backend_name:
            LOG.warn('Empty backend name')
            return

        server_line = ('\tserver {0} {1}:{2} {3} maxconn {4} '
                       'inter {5} rise {6} fall {7}'
                       .format(server.name, server.address,
                              server.port, server.check,
                              server.maxconn, server.inter,
                              server.rise, server.fall))
        self.add_lines_to_block(HaproxyBackend(backend_name), (server_line,))

    def delete_rserver(self, backend_name, server_name):
        if not backend_name:
            LOG.warn('Empty backend name')
            return

        self.del_lines_from_block(HaproxyBackend(backend_name), (server_name,))

    def enable_rserver(self, backend_name, server_name, enable=True):
        '''
            Enables or disables server in serverfarm
        '''
        if backend_name == '':
            LOG.warn('Empty backend name')
            return

        self._fetch_config()
        for block in self.config:
            if 'backend' in block and backend_name in block:
                for line in self.comfig[block]:
                    if 'server' in line and server_name in line:
                        if not enable:
                            new_line = line + ' disabled'
                        else:
                            new_lline = line.replace(' disabled', '')
                        self.config[block].remove(line)
                        self.config[block].append(new_line)
        self._apply_config()

    def add_frontend(self, fronted, backend=None):
        if fronted.name == '':
            LOG.warn('Empty fronted name')
            return
        elif fronted.bind_address == '' or fronted.bind_port == '':
            LOG.warn('Empty bind adrress or port')
            return

        self._fetch_config()
        LOG.debug('Adding frontend %s' % fronted.name)
        frontend_block = []
        frontend_block.append('\tbind %s:%s' % (fronted.bind_address,
                                           fronted.bind_port))
        frontend_block.append('\tmode %s' % fronted.mode)
        if backend is not None:
            frontend_block.append('\tdefault_backend %s' %
                                           backend.name)
        self.config['frontend %s' % fronted.name] = frontend_block
        self._apply_config()

        return fronted.name

    def add_backend(self, backend):
        if backend.name == '':
            LOG.warn('Empty backend name')
            return
        self._fetch_config()
        LOG.debug('Adding backend {0}'.format(backend.name))
        backend_block = []
        backend_block.append('\tbalance %s' % backend.balance)
        self.config['backend %s' % backend.name] = backend_block
        self._apply_config()

        return backend.name

    def delete_block(self, block):
        if block.name == '':
            LOG.warn('Empty block name')
            return

        self._fetch_config()
        for key in self.config.keys():
            if block.type in key and block.name in key:
                LOG.debug('Delete block {0} {1}'.format(block.type,
                                                        block.name))
                del self.config[key]
        self._apply_config()

    def find_string_in_any_block(self, string, block_type=None):
        self._fetch_config()
        for key in self.config:
            if block_type is None or block_type in key:
                if string in self.config[key]:
                    return True

        return False

    def _fetch_config(self):
        if not self.need_deploy:
            LOG.debug('Fetching configuration from {0}'
                      .format(self.remote_config_path))

            self.remote_control.get_file(self.remote_config_path,
                                         self.local_config_path)

            config_file = open(self.local_config_path, 'r')
            self.config = {}
            cur_block = ''
            for line in config_file:
                line = line.rstrip()

                if line.find('global') == 0:
                    cur_block = line
                    self.config[cur_block] = []
                elif line.find('defaults') == 0:
                    cur_block = line
                    self.config[cur_block] = []
                elif line.find('listen') == 0:
                    cur_block = line
                    self.config[cur_block] = []
                elif line.find('backend') == 0:
                    cur_block = line
                    self.config[cur_block] = []
                elif line.find('frontend') == 0:
                    cur_block = line
                    self.config[cur_block] = []
                else:
                    self.config[cur_block].append(line)

            config_file.close()

    def _apply_config(self):
        LOG.debug('writing configuration to %s' %
                  self.local_config_path)
        config_file = open(self.local_config_path, 'w')

        config_file.write('global\n')
        for line in (self.config.get('global') or []):
            config_file.write(line + '\n')
        config_file.write('defaults\n')
        for line in (self.config.get('defaults') or []):
            config_file.write(line + '\n')

        for block in self.config:
            if block != 'global' and block != 'defaults':
                config_file.write('%s\n' % block)
                for line in self.config[block]:
                    config_file.write('%s\n' % line)

        config_file.close()
        self.need_deploy = True

    def _validate_config(self, filepath):
        command = 'haproxy -c -f {0}'.format(filepath)
        output = self.remote_control.perform(command)[1]
        if 'Configuration file is valid' in output:
            LOG.debug('Remote configuration is valid: {0}'.format(filepath))
            return True
        else:
            LOG.error('Invalid configuration in {0}: {1}'.format(filepath,
                                                                 output))
            return False


class HaproxyConfigBlock(object):
    def __init__(self, name='', type=''):
        self.name = name
        self.type = type


class HaproxyFronted(HaproxyConfigBlock):
    def __init__(self, name=''):
        super(HaproxyFronted, self).__init__(name, 'frontend')
        self.bind_address = ''
        self.bind_port = ''
        self.default_backend = ''
        self.mode = 'http'


class HaproxyBackend(HaproxyConfigBlock):
    def __init__(self, name=''):
        super(HaproxyBackend, self).__init__(name, 'backend')
        self.mode = ''
        self.balance = 'roundrobin'


class HaproxyListen(HaproxyConfigBlock):
    def __init__(self, name=''):
        super(HaproxyListen, self).__init__(name, 'listen')
        self.mode = ''
        self.balance = 'source'


class HaproxyRserver():
    def __init__(self, name=''):
        self.name = name
        self.address = ''
        self.check = 'check'
        self.cookie = ''
        self.disabled = False
        self.error_limit = 10
        self.fall = '3'
        self.id = ''
        self.inter = 2000
        self.fastinter = 2000
        self.downinter = 2000
        self.maxconn = 32
        self.minconn = 0
        self.observe = ''
        self.on_error = ''
        self.port = ''
        self.redir = ''
        self.rise = '2'
        self.slowstart = 0
        self.source_addres = ''
        self.source_min_port = ''
        self.source_max_port = ''
        self.track = ''
        self.weight = 1
