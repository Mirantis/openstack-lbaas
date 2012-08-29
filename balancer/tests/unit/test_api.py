import unittest
import mock
import logging
import balancer.exception as exception
from openstack.common import wsgi
from balancer.api.v1 import loadbalancers
from balancer.api.v1 import nodes
from balancer.api.v1 import vips
from balancer.api.v1 import probes
from balancer.api.v1 import stickies
from balancer.api.v1 import devices
from balancer.api.v1 import router

LOG = logging.getLogger()


class TestLoadBalancersController(unittest.TestCase):
    def setUp(self):
        super(TestLoadBalancersController, self).setUp()
        self.conf = mock.Mock()
        self.controller = loadbalancers.Controller(self.conf)
        self.req = mock.Mock()

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_find_for_vm', autospec=True)
    def test_find_lb_for_vm(self, mock_lb_find_for_vm):
        mock_lb_find_for_vm.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id',
                            'X-Tenant-Name': 'fake_tenant_name'}
        resp = self.controller.findLBforVM(self.req, vm_id='123')
        self.assertTrue(mock_lb_find_for_vm.called)
        mock_lb_find_for_vm.assert_called_once_with(self.conf, '123')
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.lb_get_index', autospec=True)
    def test_index(self, mock_lb_get_index):
        mock_lb_get_index.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.index(self.req)
        self.assertTrue(mock_lb_get_index.called)
        mock_lb_get_index.assert_called_once_with(
                                    self.conf,
                                    self.req.headers.get('X-Tenant-Id', ""))
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.create_lb', autospec=True)
    def test_create(self, mock_create_lb):
        mock_create_lb.return_value = '1'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.create(self.req, {})
        self.assertTrue(mock_create_lb.called)
        mock_create_lb.assert_called_once_with(
                        self.conf,
                        {'tenant_id': self.req.headers.get('X-Tenant-Id', "")})
        self.assertEqual(resp, {'loadbalancer': {'id': '1'}})
        self.code_assert(202, self.controller.create)

    @mock.patch('balancer.core.api.delete_lb', autospec=True)
    def test_delete(self, mock_delete_lb):
        resp = self.controller.delete(self.req, 1)
        self.assertTrue(mock_delete_lb.called)
        self.code_assert(204, self.controller.delete)
        mock_delete_lb.assert_called_once_with(self.conf, 1)
        self.assertEqual(resp, None)

    @mock.patch('balancer.core.api.lb_get_data', autospec=True)
    def test_show(self, mock_lb_get_data):
        mock_lb_get_data.return_value = 'foo'
        resp = self.controller.show(self.req, 1)
        self.assertTrue(mock_lb_get_data.called)
        mock_lb_get_data.assert_called_once_with(self.conf, 1)
        self.assertEqual(resp, {'loadbalancer': 'foo'})

    @mock.patch('balancer.core.api.lb_show_details', autospec=True)
    def test_details(self, mock_lb_show_details):
        mock_lb_show_details.return_value = 'foo'
        resp = self.controller.details(self.req, 1)
        self.assertTrue(mock_lb_show_details.called)
        mock_lb_show_details.assert_called_once_with(self.conf, 1)
        self.assertEqual('foo', resp)

    @mock.patch('balancer.core.api.update_lb', autospec=True)
    def test_update(self, mock_update_lb):
        resp = self.controller.update(self.req, 1, {})
        self.assertTrue(mock_update_lb.called)
        self.code_assert(202, self.controller.update)
        mock_update_lb.assert_called_once_with(self.conf, 1, {})
        self.assertEquals(resp, {"loadbalancer": {"id": 1}})


class TestNodesController(unittest.TestCase):
    def setUp(self):
        super(TestNodesController, self).setUp()
        self.conf = mock.Mock()
        self.controller = nodes.Controller(self.conf)
        self.req = mock.Mock()

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_add_nodes', autospec=True)
    def test_create(self, mock_lb_add_nodes):
        mock_lb_add_nodes.return_value = 'foo'
        body = {'nodes': 'foo'}
        resp = self.controller.create(self.req, 1, body)
        self.assertTrue(mock_lb_add_nodes.called)
        mock_lb_add_nodes.assert_called_once_with(self.conf, 1, 'foo')
        self.assertEqual(resp, {'nodes': 'foo'})

    @mock.patch('balancer.core.api.lb_show_nodes', autospec=True)
    def test_index(self, mock_lb_show_nodes):
        mock_lb_show_nodes.return_value = 'foo'
        resp = self.controller.index(self.req, 1)
        self.assertTrue(mock_lb_show_nodes.called)
        mock_lb_show_nodes.assert_called_once_with(self.conf, 1)
        self.assertEqual(resp, {'nodes': 'foo'})

    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_show(self, mock_server_get, mock_unpack):
        mock_server_get.return_value = 'foo'
        resp = self.controller.show(self.req, '123', '123')
        self.assertTrue(mock_server_get.called)
        self.assertTrue(mock_unpack.called)
        mock_server_get.assert_called_once_with(self.conf, '123', '123')
        mock_unpack.assert_called_once_with(['foo'])
        self.assertEqual(resp, {'node': 'foo'})

    @mock.patch('balancer.core.api.lb_delete_node', autospec=True)
    def test_delete(self, mock_lb_delete_node):
        resp = self.controller.delete(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_node.called)
        mock_lb_delete_node.assert_called_once_with(self.conf, 1, 1)
        self.assertEqual(resp, None)
        self.code_assert(204, self.controller.delete)

    @mock.patch('balancer.core.api.lb_change_node_status', autospec=True)
    def test_change_node_status(self, mock_lb_change_node_status):
        mock_lb_change_node_status.return_value = {'nodeID': '1',
                                                   'status': 'Foostatus'}
        resp = self.controller.changeNodeStatus(self.req, 1, 1, 'Foostatus',
                {})
        self.assertTrue(mock_lb_change_node_status.called)
        mock_lb_change_node_status.assert_called_once_with(self.conf, 1, 1,
                                                           'Foostatus')
        self.assertFalse(hasattr(
            self.controller.changeNodeStatus, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertEqual(resp, {"node": {'nodeID': '1',
                                         'status': 'Foostatus'}})

    @mock.patch('balancer.core.api.lb_update_node', autospec=True)
    def test_update(self, mock_lb_update_node):
        req_kwargs = {'lb_id': '1',
                      'id': '1',
                      'body': {'node': 'node'}}
        mock_lb_update_node.return_value = {'nodeID': '1'}
        mock_lb_update_node.assert_called_once_with(self.conf, '1', '1',
                                                    {'node': 'node'})
        resp = self.controller.update(self.req, **req_kwargs)
        self.assertTrue(mock_lb_update_node.called)
        self.assertFalse(hasattr(self.controller.update, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertEqual(resp, {"node": {'nodeID': '1'}})



class TestVIPsController(unittest.TestCase):
    def setUp(self):
        super(TestVIPsController, self).setUp()
        self.conf = mock.Mock()
        self.controller = vips.Controller(self.conf)
        self.req = mock.Mock()

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                            autospec=True)
    def test_index0(self, mock_get, mock_unpack):
        """VIPs should be found"""
        mock_get.return_value = ['foo']
        mock_unpack.return_value = 'foo1'
        resp = self.controller.index(self.req, '1')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_unpack.called)
        mock_get.assert_called_once_with(self.conf, '1')
        mock_unpack.assert_called_once_with('foo')
        self.assertEqual(resp, {'virtualIps': ['foo1']})

    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                           autospec=True)
    def test_index1(self, mock_get):
        """Should raise exception"""
        mock_get.side_effect = exception.VirtualServerNotFound()
        with self.assertRaises(exception.VirtualServerNotFound):
            resp = self.controller.index(self.req, '1')
            self.assertEqual(resp, None)

    @mock.patch('balancer.core.api.lb_add_vip', autospec=True)
    def test_create(self, mock_lb_add_vip):
        mock_lb_add_vip.return_value = 'fakevip'
        resp = self.controller.create(self.req, 'fakelbid',
                                      {'virtualIp': 'fakebody'})
        self.assertTrue(mock_lb_add_vip.called)
        mock_lb_add_vip.assert_called_once_with(self.conf, 'fakelbid',
                                                'fakebody')
        self.assertEqual(resp, {'virtualIp': 'fakevip'})

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.virtualserver_get', autospec=True)
    def test_show(self, mock_virtualserver_get, mock_unpack_extra):
        mock_virtualserver_get.return_value = 'fakevip'
        mock_unpack_extra.return_value = 'packedfakevip'
        resp = self.controller.show(self.req, 'fakelbid', 'fakeid')
        self.assertTrue(mock_virtualserver_get.called)
        self.assertTrue(mock_unpack_extra.called)
        mock_virtualserver_get.assert_called_once_with(self.conf, 'fakeid')
        mock_unpack_extra.assert_called_once_with('fakevip')
        self.assertEqual(resp, {'virtualIp': 'packedfakevip'})

    @mock.patch('balancer.core.api.lb_delete_vip', autospec=True)
    def test_delete(self, mock_lb_delete_vip):
        resp = self.controller.delete(self.conf, 'fakelbid', 'fakeid')
        self.assertTrue(mock_lb_delete_vip.called)
        mock_lb_delete_vip.assert_called_once_with(self.conf, 'fakelbid',
                                                   'fakeid')
        self.code_assert(204, self.controller.delete)


class TestProbesController(unittest.TestCase):
    def setUp(self):
        super(TestProbesController, self).setUp()
        self.conf = mock.Mock()
        self.controller = probes.Controller(self.conf)
        self.req = mock.Mock()

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_show_probes', autospec=True)
    def test_index(self, mock_lb_show_probes):
        mock_lb_show_probes.return_value = 'foo'
        resp = self.controller.index(self.req, 1)
        self.assertTrue(mock_lb_show_probes.called)
        mock_lb_show_probes.assert_called_once_with(self.conf, 1)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.probe_get', autospec=True)
    def test_show(self, mock_lb_show_probe_by_id):
        mock_lb_show_probe_by_id.return_value = ['foo']
        mock_extra.return_value = 'foo'
        resp = self.controller.show(self.req, 1, 1)
        self.assertTrue(mock_lb_show_probe_by_id.called)
        self.assertTrue(mock_extra.called)
        mock_lb_show_probe_by_id.assert_called_once_with(self.conf, 1)
        mock_extra.assert_called_once_with(['foo'])
        self.assertEqual(resp, {'healthMonitoring': 'foo'})

    @mock.patch('balancer.core.api.lb_add_probe', autospec=True)
    def test_create(self, mock_lb_add_probe):
        mock_lb_add_probe.return_value = {'id': '2'}
        body = {'healthMonitoring': {'probe': 'foo'}}
        resp = self.controller.create(self.req, '1', body)
        self.assertTrue(mock_lb_add_probe.called)
        mock_lb_add_probe.assert_called_once_with(self.conf, '1',
                                                  {'probe': 'foo'})
        self.assertEqual(resp, {'healthMonitoring': {'id': '2'}})

    @mock.patch('balancer.core.api.lb_delete_probe', autospec=True)
    def test_delete(self, mock_lb_delete_probe):
        resp = self.controller.delete(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_probe.called)
        mock_lb_delete_probe.assert_called_once_with(self.conf, 1, 1)
        self.assertEqual(resp, None)
        self.code_assert(204, self.controller.delete)


class TestStickiesController(unittest.TestCase):
    def setUp(self):
        super(TestStickiesController, self).setUp()
        self.conf = mock.Mock()
        self.controller = stickies.Controller(self.conf)
        self.req = mock.Mock()

    def code_assert(self, code, func):
        self.assertTrue(hasattr(func, "wsgi_code"),
                "has not redifined HTTP status code")
        self.assertTrue(func.wsgi_code == code,
                "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_show_sticky', autospec=True)
    def test_index(self, mock_lb_show_sticky):
        mock_lb_show_sticky.return_value = 'foo'
        resp = self.controller.index(self.req, 1)
        self.assertTrue(mock_lb_show_sticky.called)
        mock_lb_show_sticky.assert_called_once_with(self.conf, 1)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.sticky_get', autospec=True)
    def test_show(self, mock_func):
        mock_extra.return_value = 'foo'
        resp = self.controller.show(self.req, 1, 1)
        self.assertTrue(mock_func.called)
        self.assertTrue(mock_extra.called)
        mock_func.assert_called_once_with(self.conf, 1)
        mock_extra.assert_called_once_with(mock_func.return_value)
        self.assertEqual(resp, {'sessionPersistence': 'foo'})

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.core.api.lb_add_sticky', autospec=True)
    def test_create(self, mock_lb_add_sticky, mock_unpack):
        mock_unpack.return_value = '1'
        mock_lb_add_sticky.return_value = ['1']
        resp = self.controller.create(self.req, 1,
                {'sessionPersistence': 'foo'})
        self.assertTrue(mock_lb_add_sticky.called)
        mock_lb_add_sticky.assert_called_once_with(self.conf, 1,
                                                {'sessionPersistence': 'foo'})
        mock_unpack.assert_called_once_with(['1'])
        self.assertEqual(resp, {"sessionPersistence": "1"})

    @mock.patch('balancer.core.api.lb_delete_sticky', autospec=True)
    def test_delete(self, mock_lb_delete_sticky):
        resp = self.controller.delete(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_sticky.called)
        mock_lb_delete_sticky.assert_called_once_with(self.conf, 1, 1)
        self.assertEqual(resp, None)
        self.code_assert(204, self.controller.delete)


class TestDeviceController(unittest.TestCase):
    def setUp(self):
        self.conf = mock.Mock()
        self.controller = devices.Controller(self.conf)
        self.req = mock.Mock()

    @mock.patch('balancer.core.api.device_get_index', autospec=True)
    def test_index(self, mock_device_get_index):
        mock_device_get_index.return_value = 'foo'
        resp = self.controller.index(self.req)
        self.assertTrue(mock_device_get_index.called)
        mock_device_get_index.assert_called_once_with(self.conf)
        self.assertEqual({'devices': 'foo'}, resp)

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.core.api.device_create', autospec=True)
    def test_create(self, mock_device_create, mock_unpack):
        mock_device_create.return_value = ['foo']
        mock_unpack.return_value = 'foo'
        res = self.controller.create(self.req, {'foo': 'foo'})
        self.assertTrue(mock_device_create.called)
        mock_device_create.assert_called_once_with(self.conf, foo='foo')
        mock_unpack.assert_called_once_with(['foo'])
        self.assertEqual({'device': 'foo'}, res)

    @mock.patch('balancer.core.api.device_delete', autospec=True)
    def test_delete(self, mock_device_delete):
        resp = self.controller.delete(self.req, 1)
        self.assertTrue(mock_device_delete.called)
        mock_device_delete.assert_called_once_with(self.conf, 1)
        self.assertTrue(hasattr(self.controller.delete, "wsgi_code"),
                                "has not redifined HTTP status code")
        self.assertTrue(self.controller.delete.wsgi_code == 204,
        "incorrect HTTP status code")
        self.assertEqual(None, resp)

    @unittest.skip('need to implement Controller.device_info')
    @mock.patch('balancer.core.api.device_info', autospec=True)
    def test_info(self, mock_device_info):
        mock_device_info.return_value = 'foo'
        resp = self.controller.device_info(self.req)
        self.assertTrue(mock_device_info.called)
        mock_device_info.assert_called_once_with()
        self.assertEqual({'devices': 'foo'}, resp)

    @mock.patch('balancer.core.api.device_show_algorithms')
    def test_show_algorithms_0(self, mock_core_api):
        resp = self.controller.show_algorithms(self.req)
        self.assertTrue(mock_core_api.called)

    @mock.patch('balancer.core.api.device_show_protocols')
    def test_show_protocols(self, mock_core_api):
        resp = self.controller.show_protocols(self.req)
        self.assertTrue(mock_core_api.called)


class TestRouter(unittest.TestCase):
    def setUp(self):
        config = mock.MagicMock(spec=dict)
        self.obj = router.API(config)

    def test_mapper(self):
        list_of_methods = (
            ("/loadbalancers", "GET", loadbalancers.Controller, "index"),
            ("/loadbalancers/find_for_VM/{vm_id}", "GET",
                loadbalancers.Controller, "findLBforVM"),
            ("/loadbalancers/{id}", "GET", loadbalancers.Controller,
                "show"),
            ("/loadbalancers/{id}/details", "GET", loadbalancers.Controller,
                "details"),
            ("/loadbalancers/{id}", "DELETE", loadbalancers.Controller,
                "delete"),
            ("/loadbalancers/{id}", "PUT", loadbalancers.Controller,
                "update"),
            ("/loadbalancers/{lb_id}/nodes", "POST", nodes.Controller,
                "create"),
            ("/loadbalancers/{lb_id}/nodes", "GET", nodes.Controller,
                "index"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "DELETE",
                nodes.Controller, "delete"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "GET",
                nodes.Controller, "show"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "PUT",
                nodes.Controller, "update"),
            ("/loadbalancers/{lb_id}/nodes/{id}/{status}", "PUT",
                nodes.Controller, "changeNodeStatus"),
            ("/loadbalancers/{lb_id}/healthMonitoring", "GET",
                probes.Controller, "index"),
            ("/loadbalancers/{lb_id}/healthMonitoring/{id}",
                "GET", probes.Controller, "show"),
            ("/loadbalancers/{lb_id}/healthMonitoring", "POST",
                probes.Controller, "create"),
            ("/loadbalancers/{lb_id}/healthMonitoring/{id}", "DELETE",
                probes.Controller, "delete"),
            ("/loadbalancers/{lb_id}/sessionPersistence", "GET",
                stickies.Controller, "index"),
            ("/loadbalancers/{lb_id}/sessionPersistence/{id}", "GET",
                stickies.Controller, "show"),
            ("/loadbalancers/{lb_id}/sessionPersistence", "POST",
                stickies.Controller, "create"),
            ("/loadbalancers/{lb_id}/sessionPersistence/{id}",
                "DELETE", stickies.Controller, "delete"),

            # Virtual IPs
            ("/loadbalancers/{lb_id}/virtualIps", "GET",
                vips.Controller, "index"),
            ("/loadbalancers/{lb_id}/virtualIps", "POST",
                vips.Controller, "create"),
            ("/loadbalancers/{lb_id}/virtualIps/{id}", "GET",
                vips.Controller, "show"),
            ("/loadbalancers/{lb_id}/virtualIps/{id}", "DELETE",
                vips.Controller, "delete"),

            ("/loadbalancers", "POST", loadbalancers.Controller, "create"),
            ("/devices", "GET", devices.Controller, "index"),
            ("/devices/{id}", "GET", devices.Controller, "show"),
            ("/devices/{id}/info", "GET", devices.Controller, "device_info"),
            ("/devices", "POST", devices.Controller, "create"),
            ("/devices/{id}", "DELETE", devices.Controller, "delete"),
        )
        for url, method, controller, action in list_of_methods:
            LOG.info('Verifying %s to %s', method, url)
            m = self.obj.map.match(url, {"REQUEST_METHOD": method})
            self.assertTrue(m is not None)
            controller0 = m.pop('controller')
            action0 = m.pop('action')
            self.assertTrue(isinstance(controller0, wsgi.Resource))
            self.assertTrue(isinstance(controller0.controller,
                controller))
            self.assertEquals(action0, action)
            mok = mock.mocksignature(getattr(controller, action))
            if method == "POST" or method == "PUT":
                m['body'] = {}
            try:
                mok('SELF', 'REQUEST', **m)
            except TypeError:
                self.fail('Arguments in route "%s %s" does not match %s.%s.%s '
                            'signature' % (method, url, controller.__module__,
                                       controller.__name__, action))
