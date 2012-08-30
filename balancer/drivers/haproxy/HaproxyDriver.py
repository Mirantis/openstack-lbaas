# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
from balancer.drivers.base_driver import BaseDriver
from balancer.drivers.haproxy.RemoteControl import RemoteConfig, RemoteService
from balancer.drivers.haproxy.RemoteControl import RemoteInterface
from balancer.drivers.haproxy.RemoteControl import RemoteSocketOperation


logger = logging.getLogger(__name__)


class HaproxyDriver(BaseDriver):
    def __init__(self, conf, device_ref):
        super(HaproxyDriver, self).__init__(conf, device_ref)
        device_extra = self.device_ref.get('extra') or {}
        if ((device_extra.get('local_conf_dir') is None) or
                (device_extra['local_conf_dir'] == "None")):
            self.localpath = '/tmp/'
        else:
            self.localpath = device_extra.get('localpath')
        if ((device_extra.get('remote_conf_dir') is None) or
                (device_extra['remote_conf_dir'] == "None")):
            self.remotepath = '/etc/haproxy/'
        else:
            self.remotepath = device_extra.get('remote_conf_dir')
        if ((device_extra.get('remote_conf_file') is None) or
                (device_extra['remote_conf_file'] == "None")):
            self.configfilename = 'haproxy.cfg'
        else:
            self.configfilename = device_extra.get('remote_conf_file')
        if ((device_extra.get('interface') is None) or
                (device_extra['interface'] == "None")):
            self.interface = 'eth0'
        else:
            self.interface = device_extra.get('interface')
        if ((device_extra.get('socket') is None) or
                (device_extra['socket'] == "None")):
            self.haproxy_socket = '/tmp/haproxy.sock'
        else:
            self.haproxy_socket = device_extra['socket']
        self.config_file = None
        self.config_was_deployed = True

    def _get_config(self):
        if self.config_file == None:
            self.config_file = HaproxyConfigFile('%s/%s' % (self.localpath,
                                            self.configfilename))
            remote = RemoteConfig(self.device_ref, self.localpath,
                                  self.remotepath, self.configfilename)
            remote.get_config()
        self.config_was_deployed = False
        logger.debug("Marking as not deployed")
        return self.config_file

    def add_probe_to_server_farm(self, serverfarm, probe):
        '''
            Haproxy supports only tcp (connect),
            http and https (limited) probes
        '''
        probe_type = probe['type'].lower()
        if probe_type not in ('http', 'https', 'tcp', 'connect'):
            logger.debug('[HAPROXY] unsupported probe type %s, exit',
                         probe_type)
            return

        backend = HaproxyBackend()
        backend.name = serverfarm['id']

        new_lines = []
        if probe_type == 'http':
            option = 'option httpchk'
            method = probe.get('method')
            option = option + ' ' + (method if method else 'GET')

            HTTPurl = probe.get('path', '')
            option = option + ' ' + (HTTPurl if HTTPurl else '/')

            new_lines.append(option)

            # TODO: add handling of 'expected' field
            # from probe ('http-check expect ...')
        elif probe_type == 'tcp' or probe_type == 'connect':
            new_lines.append('option httpchk')
        elif probe_type == 'https':
            new_lines.append('option ssl-hello-chk')

        if new_lines:
            config_file = self._get_config()
            config_file.add_lines_to_backend_block(backend, new_lines)

    def delete_probe_from_server_farm(self, serverfarm, probe):
        backend = HaproxyBackend()
        backend.name = serverfarm['id']

        probe_type = probe['type'].lower()
        del_lines = []
        if probe_type in ('http', 'tcp', 'connect'):
            del_lines = ['option httpchk', 'http-check expect']
        elif probe_type == 'https':
            del_lines = ['option ssl-hello-chk', ]

        if del_lines:
            config_file = self._get_config()
            config_file.del_lines_from_backend_block(backend, del_lines)

    '''
        For compatibility with drivers for other devices
    '''
    def create_real_server(self, rserver):
        pass

    def delete_real_server(self, rserver):
        pass

    def create_probe(self, probe):
        pass

    def delete_probe(self, probe):
        pass

    def create_stickiness(self, sticky):
        pass

    def delete_stickiness(self, sticky):
        pass

    def add_real_server_to_server_farm(self, serverfarm, rserver):
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        haproxy_rserver.weight = rserver.get('weight') or 1
        haproxy_rserver.address = rserver['address']
        haproxy_rserver.port = rserver.get('port') or 0
        haproxy_rserver.maxconn = rserver['extra'].get('maxCon') or 10000
        #Modify remote config file, check and restart remote haproxy
        logger.debug('[HAPROXY] Creating rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, haproxy_serverfarm.name))

        config_file = self._get_config()
        config_file.add_rserver_to_backend_block(haproxy_serverfarm,
                                             haproxy_rserver)

    def delete_real_server_from_server_farm(self, serverfarm, rserver):
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        #Modify remote config file, check and restart remote haproxy
        logger.debug('[HAPROXY] Deleting rserver %s in the '
                     'backend block %s' %
                     (haproxy_rserver.name, haproxy_serverfarm.name))
        config_file = self._get_config()
        config_file.del_rserver_from_backend_block(haproxy_serverfarm,
                                               haproxy_rserver)

    def create_virtual_ip(self, virtualserver, serverfarm):
        if not bool(virtualserver['id']):
            logger.error('[HAPROXY] Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver['id']
        haproxy_virtualserver.bind_address = virtualserver['address']
        haproxy_virtualserver.bind_port = virtualserver.get('port') or 0
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        logger.debug('[HAPROXY] create VIP %s' % haproxy_serverfarm.name)
        #Add new IP address
        remote_interface = RemoteInterface(self.device_ref,
                                           haproxy_virtualserver)
        remote_interface.add_ip()
        #Modify remote config file, check and restart remote haproxy
        config_file = self._get_config()
        config_file.add_frontend(haproxy_virtualserver, haproxy_serverfarm)

    def delete_virtual_ip(self, virtualserver):
        logger.debug('[HAPROXY] delete VIP')
        if not bool(virtualserver['id']):
            logger.error('[HAPROXY] Virtualserver name is empty')
            return 'VIRTUALSERVER NAME ERROR'
        haproxy_virtualserver = HaproxyFronted()
        haproxy_virtualserver.name = virtualserver['id']
        haproxy_virtualserver.bind_address = virtualserver['address']
        config_file = self._get_config()
        #Check ip for using in the another frontend
        if not config_file.find_string_in_the_block('frontend',
            haproxy_virtualserver.bind_address):
            logger.debug('[HAPROXY] ip %s is not used in any '
                         'frontend, deleting it from remote interface' %
                         haproxy_virtualserver.bind_address)
            remote_interface = RemoteInterface(self.device_ref,
                                               haproxy_virtualserver)
            remote_interface.del_ip()
        config_file.delete_block(haproxy_virtualserver)

    def get_statistics(self, serverfarm, rserver):
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        remote_socket = RemoteSocketOperation(self.device_ref,
                                        haproxy_serverfarm, haproxy_rserver,
                                        self.interface, self.haproxy_socket)
        out = remote_socket.get_statistics()
        statistics = {}
        if out:
            status_line = out.split(",")
            statistics['weight'] = status_line[18]
            statistics['state'] = status_line[17]
            statistics['connCurrent'] = [4]
            statistics['connTotal'] = [7]
            statistics['connFail'] = [13]
            statistics['connMax'] = [5]
            statistics['connRateLimit'] = [34]
            statistics['bandwRateLimit'] = [35]
# NOTE: broken because use indeterminate state variable
#        logger.debug('[HAPROXY] statistics rserver state is \'%s\'',
#                statistics.state)
        return statistics

    def suspend_real_server(self, serverfarm, rserver):
        self.operationWithRServer(serverfarm, rserver, 'suspend')

    def activate_real_server(self, serverfarm, rserver):
        self.operationWithRServer(serverfarm, rserver, 'activate')

    def operationWithRServer(self, serverfarm, rserver, type_of_operation):
        haproxy_rserver = HaproxyRserver()
        haproxy_rserver.name = rserver['id']
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']
        config_file = self._get_config()

        remote_socket = RemoteSocketOperation(self.device_ref,
                                        haproxy_serverfarm, haproxy_rserver,
                                        self.interface, self.haproxy_socket)
        if type_of_operation == 'suspend':
            config_file.enable_disable_reserver_in_backend_block(
                             haproxy_serverfarm, haproxy_rserver, 'disable')
            remote_socket.suspend_server()
        elif type_of_operation == 'activate':
            config_file.enable_disable_reserver_in_backend_block(
                             haproxy_serverfarm, haproxy_rserver, 'enable')
            remote_socket.activate_server()

    def create_server_farm(self, serverfarm, predictor):
        if not bool(serverfarm['id']):
            logger.error('[HAPROXY] Serverfarm name is empty')
            return 'SERVERFARM FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']

        for p in predictor:
            if p.get('type').lower() == 'roundrobin':
                haproxy_serverfarm.balance = 'roundrobin'
            elif p.get('type').lower() == 'leastconnections':
                haproxy_serverfarm.balance = 'leastconn'
            elif p.get('type').lower() == 'hashaddr':
                haproxy_serverfarm.balance = 'source'
            elif p.get('type').lower() == 'hashurl':
                haproxy_serverfarm.balance = 'uri'

        config_file = self._get_config()
        config_file.add_backend(haproxy_serverfarm)

    def delete_server_farm(self, serverfarm):
        if not bool(serverfarm['id']):
            logger.error('[HAPROXY] Serverfarm name is empty')
            return 'SERVER FARM NAME ERROR'
        haproxy_serverfarm = HaproxyBackend()
        haproxy_serverfarm.name = serverfarm['id']

        config_file = self._get_config()
        config_file.delete_block(haproxy_serverfarm)

    """
       Putting config back on device
    """
    def finalize_config(self):
        if not self.config_was_deployed:
            logger.debug("[HAPROXY] Deploying configuration")
            remote = RemoteConfig(self.device_ref, self.localpath,
                                  self.remotepath, self.configfilename)
            remote.put_config()
            if remote.validate_config():
                service = RemoteService(self.device_ref)
                if service.restart():
                    self.config_was_deployed = True
                else:
                    logger.error("[HAPROXY] failed to restart haproxy")
                    self.config_was_deployed = False
            else:
                logger.error('[HAPROXY] Configurations has failed validation')
                return False
        return True


class HaproxyConfigBlock:
    def __init__(self):
        self.name = ''
        self.type = ''


class HaproxyFronted(HaproxyConfigBlock):
    def __init__(self):
        self.type = 'frontend'
        self.bind_address = ''
        self.bind_port = ''
        self.default_backend = ''
        self.mode = 'http'


class HaproxyBackend(HaproxyConfigBlock):
    def __init__(self):
        self.type = 'backend'
        self.mode = ''
        self.balance = 'roundrobin'


class HaproxyListen(HaproxyConfigBlock):
    def __init__(self):
        self.type = 'listen'
        self.name = ''
        self.mode = ''
        self.balance = 'source'


class HaproxyRserver():
    def __init__(self):
        self.name = ''
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


class HaproxyConfigFile:
    def __init__(self, haproxy_config_file_path='/tmp/haproxy.cfg'):
        self.haproxy_config_file_path = haproxy_config_file_path

    def get_config_file(self):
        return self.haproxy_config_file_path

    def add_lines_to_backend_block(self, HaproxyBackend, NewLines):
        '''
             Add lines to backend section config file
        '''
        new_config_file = self._read_config_file()
        logger.debug('[HAPROXY] add lines to backend %s' % HaproxyBackend.name)
        for i in new_config_file.keys():
            if (i.find(HaproxyBackend.type) == 0 and
                    i.find('%s' % HaproxyBackend.name) >= 0):
                for j in NewLines:
                    logger.debug('[HAPROXY] add line \'%s\'' % j)
                    new_config_file[i].append("\t%s" % j)
        self._write_config_file(new_config_file)

    def del_lines_from_backend_block(self, HaproxyBackend, DelLines):
        '''
            Delete lines from backend section config file
        '''
        new_config_file = self._read_config_file()
        logger.debug('[HAPROXY] delete lines from backend %s',
                HaproxyBackend.name)
        for i in new_config_file.keys():
            if (i.find(HaproxyBackend.type) == 0 and
                    i.find('%s' % HaproxyBackend.name) >= 0):
                logger.debug('[HAPROXY] found %s' % new_config_file[i])
                for s in DelLines:
                    for j in new_config_file[i]:
                        if j.find(s) >= 0:
                            logger.debug('[HAPROXY] delete line \'%s\'' % s)
                            new_config_file[i].remove(j)
        self._write_config_file(new_config_file)

    def add_rserver_to_backend_block(self, HaproxyBackend, HaproxyRserver):
        '''
            Add real server to backend section config file
        '''
        new_config_file = self._read_config_file()
        logger.debug('[HAPROXY] backend %s rserver %s' % (HaproxyBackend.name,
                                                          HaproxyRserver.name))
        if HaproxyBackend.name == '':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        for i in new_config_file.keys():
            if i.find(HaproxyBackend.type) == 0 and i.find('%s' %
                                          HaproxyBackend.name) >= 0:
                new_config_file[i].append('\tserver %s %s:%s %s maxconn %s'
                                              ' inter %s rise %s fall %s' %
                (HaproxyRserver.name, HaproxyRserver.address,
                HaproxyRserver.port, HaproxyRserver.check,
                HaproxyRserver.maxconn, HaproxyRserver.inter,
                HaproxyRserver.rise, HaproxyRserver.fall))
        self._write_config_file(new_config_file)

    def del_rserver_from_backend_block(self, HaproxyBackend, HaproxyRserver):
        '''
            Delete real server to backend section config file
        '''
        new_config_file = self._read_config_file()
        logger.debug('[HAPROXY] From backend %s delete rserver %s' %
                          (HaproxyBackend.name, HaproxyRserver.name))
        if HaproxyBackend.name == '':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        for i in new_config_file.keys():
            if i.find(HaproxyBackend.type) == 0 and i.find('%s' %
                                         HaproxyBackend.name) >= 0:
                for j in new_config_file[i]:
                    logger.debug('[HAPROXY] found %s' % new_config_file[i])
                    if (j.find('server') >= 0 and
                        j.find(HaproxyRserver.name) >= 0):
                        new_config_file[i].remove(j)
        self._write_config_file(new_config_file)

    def enable_disable_reserver_in_backend_block(self, HaproxyBackend,
                                HaproxyRserver, type_of_operation):
        '''
            Disable/Enable server in the backend section config file
        '''
        new_config_file = self._read_config_file()
        logger.debug('[HAPROXY] backend %s rserver %s' % (HaproxyBackend.name,
                                                          HaproxyRserver.name))
        if HaproxyBackend.name == '':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        for i in new_config_file.keys():
            if i.find(HaproxyBackend.type) == 0 and i.find('%s' %
                                         HaproxyBackend.name) >= 0:
                for j in new_config_file[i]:
                    logger.debug('[HAPROXY] found %s' % new_config_file[i])
                    if 'server' in j and HaproxyRserver.name in j:
                        if type_of_operation == 'disable':
                            tmp_str = ('%s disabled' % j)
                        elif type_of_operation == 'enable':
                            tmp_str = j.replace(' disabled', '')
                        new_config_file[i].remove(j)
                        new_config_file[i].append(tmp_str)
        self._write_config_file(new_config_file)

    def add_frontend(self, HaproxyFronted, HaproxyBackend=None):
        '''
            Add frontend section to haproxy config file
        '''
        new_config_file = self._read_config_file()
        if HaproxyFronted.name == '':
            logger.error('[HAPROXY] Empty fronted name')
            return 'FRONTEND NAME ERROR'
        if HaproxyFronted.bind_address == '' or HaproxyFronted.bind_port == '':
            logger.error('[HAPROXY] Empty bind adrress or port')
            return 'FRONTEND ADDRESS OR PORT ERROR'
        logger.debug('[HAPROXY] Adding frontend %s' % HaproxyFronted.name)
        new_config_block = []
        new_config_block.append('\tbind %s:%s' % (HaproxyFronted.bind_address,
                                                     HaproxyFronted.bind_port))
        new_config_block.append('\tmode %s' % HaproxyFronted.mode)
        if HaproxyBackend is not None:
            new_config_block.append('\tdefault_backend %s' %
                                           HaproxyBackend.name)
        new_config_file['frontend %s' % HaproxyFronted.name] = new_config_block
        self._write_config_file(new_config_file)
        return HaproxyFronted.name

    def delete_block(self, HaproxyBlock):
        '''
            Delete fronend section from haproxy config file
        '''
        new_config_file = self._read_config_file()
        if HaproxyBlock.name == '':
            logger.error('[HAPROXY] Empty block name')
            return 'BLOCK NAME ERROR'
        logger.debug('[HAPROXY] Try to delete block %s %s' %
                         (HaproxyBlock.type, HaproxyBlock.name))
        for i in new_config_file.keys():
            if i.find(HaproxyBlock.type) == 0 and i.find('%s' %
                                         HaproxyBlock.name) >= 0:
                logger.debug('[HAPROXY] Delete block %s %s' %
                          (HaproxyBlock.type, HaproxyBlock.name))
                del new_config_file[i]
        self._write_config_file(new_config_file)

    def find_string_in_the_block(self, block_type, check_string):
        """
            Find string in the block
        """
        new_config_file = self._read_config_file()
        for i in new_config_file.keys():
            if (i.find(block_type) == 0 and
                        new_config_file[i].find(check_string) >= 0):
                return True
            else:
                return False

    def add_backend(self, HaproxyBackend):
        '''
            Add backend section to haproxy config file
        '''
        new_config_file = self._read_config_file()
        if HaproxyBackend.name == '':
            logger.error('[HAPROXY] Empty backend name')
            return 'BACKEND NAME ERROR'
        logger.debug('[HAPROXY] Adding backend')
        new_config_block = []
        new_config_block.append('\tbalance %s' % HaproxyBackend.balance)
        new_config_file['backend %s' % HaproxyBackend.name] =\
                                                         new_config_block
        self._write_config_file(new_config_file)
        return HaproxyBackend.name

    def _read_config_file(self):
        haproxy_config_file = open(self.haproxy_config_file_path, 'r')
        config_file = {}
        block_name = ''
        current_block = []
        for line in haproxy_config_file:
            if not line.strip():
                continue
            tmp_line = line.strip()
            if tmp_line.find('global') == 0:
                config_file[block_name] = current_block
                block_name = line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('defaults') == 0:
                config_file[block_name] = current_block
                block_name = line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('listen') == 0:
                config_file[block_name] = current_block
                block_name = line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('backend') == 0:
                config_file[block_name] = current_block
                block_name = line.rstrip()
                current_block = []
                continue
            elif tmp_line.find('frontend') == 0:
                config_file[block_name] = current_block
                block_name = line.rstrip()
                current_block = []
                continue
            else:
                current_block.append(line.rstrip())
        #Writing last block
        config_file[block_name] = current_block
        haproxy_config_file.close()
        return config_file

    def _write_config_file(self, config_file):
        haproxy_config_file = open(self.haproxy_config_file_path, 'w+')
        logger.debug('[HAPROXY] writing configuration to %s' %
                                            self.haproxy_config_file_path)
        haproxy_config_file.write('global\n')
        for v in config_file['global']:
            haproxy_config_file.write('%s\n' % v)
        del config_file['global']
        haproxy_config_file.write('defaults\n')
        for v in config_file['defaults']:
            haproxy_config_file.write('%s\n' % v)
        del config_file['defaults']
        for k, v in sorted(config_file.iteritems()):
            haproxy_config_file.write('%s\n' % k)
            for out_line in v:
                haproxy_config_file.write('%s\n' % out_line)
        haproxy_config_file.close()

if __name__ == '__main__':
    pass
