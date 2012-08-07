import unittest
import mock
import logging
import balancer.exception as exception
from openstack.common import wsgi
from balancer.api.v1 import loadbalancers
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
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.lb_get_index', autospec=True)
    def test_index(self, mock_lb_get_index):
        mock_lb_get_index.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.index(self.req)
        self.assertTrue(mock_lb_get_index.called)
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.create_lb', autospec=True)
    @mock.patch('balancer.db.api.loadbalancer_create', autospec=True)
    def test_create(self, mock_loadbalancer_create, mock_create_lb):
        mock_loadbalancer_create.return_value = {'id': '1'}
        mock_create_lb.return_value = {'id': '1'}
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.create(self.req, {})
        self.assertTrue(mock_loadbalancer_create.called)
        self.assertTrue(mock_create_lb.called)
        self.assertEqual(resp, {'loadbalancer': {'id': '1'}})
        self.assertTrue(hasattr(self.controller.create, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.create.wsgi_code == 202,
        "incorrect HTTP status code")

    @mock.patch('balancer.core.api.delete_lb', autospec=True)
    def test_delete(self, mock_delete_lb):
        resp = self.controller.delete(self.req, 1)
        self.assertTrue(mock_delete_lb.called)
        self.code_assert(204, self.controller.delete)

    @mock.patch('balancer.core.api.lb_get_data', autospec=True)
    def test_show(self, mock_lb_get_data):
        mock_lb_get_data.return_value = 'foo'
        resp = self.controller.show(self.req, 1)
        self.assertTrue(mock_lb_get_data.called)
        self.assertEqual(resp, {'loadbalancer': 'foo'})

    @mock.patch('balancer.core.api.lb_show_details', autospec=True)
    def test_show_details(self, mock_lb_show_details):
        mock_lb_show_details.return_value = 'foo'
        resp = self.controller.showDetails(self.req, 1)
        self.assertTrue(mock_lb_show_details.called)
        self.assertEqual('foo', resp)

    @mock.patch('balancer.core.api.update_lb', autospec=True)
    def test_update(self, mock_update_lb):
        resp = self.controller.update(self.req, 1, {})
        self.assertTrue(mock_update_lb.called)
        self.assertEquals(resp, {"loadbalancer": {"id": 1}})
        self.assertTrue(hasattr(self.controller.update, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.update.wsgi_code == 202,
            "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_add_nodes', autospec=True)
    def test_add_nodes(self, mock_lb_add_nodes):
        mock_lb_add_nodes.return_value = 'foo'
        body = {'nodes': 'foo'}
        resp = self.controller.addNodes(self.req, 1, body)
        self.assertTrue(mock_lb_add_nodes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_show_nodes', autospec=True)
    def test_show_nodes(self, mock_lb_show_nodes):
        mock_lb_show_nodes.return_value = 'foo'
        resp = self.controller.showNodes(self.req, 1)
        self.assertTrue(mock_lb_show_nodes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_show_node(self, mock_server_get, mock_unpack):
        mock_server_get.return_value = 'foo'
        resp = self.controller.showNode(self.req, '123', '123')
        self.assertTrue(mock_server_get.called)
        self.assertTrue(mock_unpack.called)
        self.assertEqual(resp, {'node': 'foo'})

    @mock.patch('balancer.core.api.lb_delete_node', autospec=True)
    def test_delete_node(self, mock_lb_delete_node):
        resp = self.controller.deleteNode(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_node.called)
        self.code_assert(204, self.controller.deleteNode)

    @mock.patch('balancer.core.api.lb_change_node_status', autospec=True)
    def test_change_node_status(self, mock_lb_change_node_status):
        resp = self.controller.changeNodeStatus(self.req, 1, 1, 'Foostatus')
        self.assertTrue(mock_lb_change_node_status.called)
        self.assertFalse(hasattr(
            self.controller.changeNodeStatus, "wsgi_code"),
            "has not redifined HTTP status code")

    @mock.patch('balancer.core.api.lb_update_node', autospec=True)
    def test_update_node(self, mock_lb_update_node):
        req_kwargs = {'lb_id': '1',
                      'id': '1',
                      'body': {'node': 'node'}}
        resp = self.controller.updateNode(self.req, **req_kwargs)
        self.assertTrue(mock_lb_update_node.called)
        self.assertFalse(hasattr(self.controller.updateNode, "wsgi_code"),
            "has not redifined HTTP status code")

    @mock.patch('balancer.core.api.lb_show_probes', autospec=True)
    def test_show_monitoring(self, mock_lb_show_probes):
        mock_lb_show_probes.return_value = 'foo'
        resp = self.controller.showMonitoring(self.req, 1)
        self.assertTrue(mock_lb_show_probes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.db.api.probe_get', autospec=True)
    def test_show_probe_by_id(self, mock_lb_show_probe_by_id):
        self.controller.showProbe(self.req, 1, 1)
        self.assertTrue(mock_lb_show_probe_by_id.called)

    @mock.patch('balancer.core.api.lb_add_probe', autospec=True)
    def test_add_probe(self, mock_lb_add_probe):
        mock_lb_add_probe.return_value = {'id': '2'}
        body = {'healthMonitoring': {'probe': 'foo'}}
        resp = self.controller.addProbe(self.req, '1', body)
        self.assertTrue(mock_lb_add_probe.called)
        mock_lb_add_probe.assert_called_once_with(self.conf, '1',
                                                  {'probe': 'foo'})
        self.assertEqual(resp, {'healthMonitoring': {'id': '2'}})

    @mock.patch('balancer.core.api.lb_delete_probe', autospec=True)
    def test_delete_probe(self, mock_lb_delete_probe):
        resp = self.controller.deleteProbe(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_probe.called)
        self.code_assert(204, self.controller.deleteProbe)

    @mock.patch('balancer.core.api.lb_show_sticky', autospec=True)
    def test_show_stickiness(self, mock_lb_show_sticky):
        mock_lb_show_sticky.return_value = 'foo'
        resp = self.controller.showStickiness(self.req, 1)
        self.assertTrue(mock_lb_show_sticky.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.db.api.sticky_get', autospec=True)
    def test_show_sticky(self, mock_func):
        self.controller.showSticky(self.req, 1, 1)
        self.assertTrue(mock_func.called)

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.core.api.lb_add_sticky', autospec=True)
    def test_add_sticky(self, mock_lb_add_sticky, mock_unpack):
        mock_unpack.return_value = '1'
        resp = self.controller.addSticky(self.req, 1,
                {'sessionPersistence': 'foo'})
        self.assertTrue(mock_lb_add_sticky.called)
        self.assertEqual(resp, {"sessionPersistence": "1"})

    @mock.patch('balancer.core.api.lb_delete_sticky', autospec=True)
    def test_delete_sticky(self, mock_lb_delete_sticky):
        resp = self.controller.deleteSticky(self.req, 1, 1)
        self.assertTrue(mock_lb_delete_sticky.called)
        self.code_assert(204, self.controller.deleteSticky)

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                            autospec=True)
    def test_show_vips0(self, mock_get, mock_unpack):
        """VIPs should be found"""
        mock_get.return_value = ['foo']
        mock_unpack.return_value = 'foo1'
        resp = self.controller.showVIPs(self.req, '1')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_unpack.called)
        self.assertEqual(resp, {'vips': ['foo1']})

    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                           autospec=True)
    def test_show_vips1(self, mock_get):
        """Should raise exception"""
        mock_get.side_effect = exception.VirtualServerNotFound()
        with self.assertRaises(exception.VirtualServerNotFound):
            self.controller.showVIPs(self.req, '1')


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
        self.assertEqual({'devices': 'foo'}, resp)

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.core.api.device_create', autospec=True)
    def test_create(self, mock_device_create, mock_unpack):
        mock_unpack.return_value = 'foo'
        res = self.controller.create(self.req, {})
        self.assertTrue(mock_device_create.called)
        self.assertEqual({'device': 'foo'}, res)

    @mock.patch('balancer.core.api.device_delete', autospec=True)
    def test_delete(self, mock_device_delete):
        resp = self.controller.delete(self.req, 1)
        self.assertTrue(mock_device_delete.called)
        self.assertTrue(hasattr(self.controller.delete, "wsgi_code"),
                                "has not redifined HTTP status code")
        self.assertTrue(self.controller.delete.wsgi_code == 204,
        "incorrect HTTP status code")

    @unittest.skip('need to implement Controller.device_info')
    @mock.patch('balancer.core.api.device_info', autospec=True)
    def test_info(self, mock_device_info):
        mock_device_info.return_value = 'foo'
        resp = self.controller.device_info(self.req)
        self.assertTrue(mock_device_info.called)
        self.assertEqual({'devices': 'foo'}, resp)


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
                "showDetails"),
            ("/loadbalancers/{id}", "DELETE", loadbalancers.Controller,
                "delete"),
            ("/loadbalancers/{id}", "PUT", loadbalancers.Controller,
                "update"),
            ("/loadbalancers/{id}/nodes", "POST", loadbalancers.Controller,
                "addNodes"),
            ("/loadbalancers/{id}/nodes", "GET", loadbalancers.Controller,
                "showNodes"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "DELETE",
                loadbalancers.Controller, "deleteNode"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "GET",
                loadbalancers.Controller, "showNode"),
            ("/loadbalancers/{lb_id}/nodes/{id}", "PUT",
                loadbalancers.Controller, "updateNode"),
            ("/loadbalancers/{lb_id}/nodes/{id}/{status}", "PUT",
                loadbalancers.Controller, "changeNodeStatus"),
            ("/loadbalancers/{id}/healthMonitoring", "GET",
                loadbalancers.Controller, "showMonitoring"),
            ("/loadbalancers/{lb_id}/healthMonitoring/{id}",
                "GET", loadbalancers.Controller, "showProbe"),
            ("/loadbalancers/{id}/healthMonitoring", "POST",
                loadbalancers.Controller, "addProbe"),
            ("/loadbalancers/{lb_id}/healthMonitoring/{id}", "DELETE",
                loadbalancers.Controller, "deleteProbe"),
            ("/loadbalancers/{id}/sessionPersistence", "GET",
                loadbalancers.Controller, "showStickiness"),
            ("/loadbalancers/{lb_id}/sessionPersistence/{id}", "GET",
                loadbalancers.Controller, "showSticky"),
            ("/loadbalancers/{id}/sessionPersistence", "POST",
                loadbalancers.Controller, "addSticky"),
            ("/loadbalancers/{lb_id}/sessionPersistence/{id}",
                "DELETE", loadbalancers.Controller, "deleteSticky"),
            ("/loadbalancers/{id}/virtualips", "GET",
                loadbalancers.Controller, "showVIPs"),
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
                try:
                    if "status" not in m:
                        m['body'] = {}
                    print m
                    mok('SELF', 'REQUEST', **m)
                except TypeError:
                    self.fail('Arguments in route "%s %s" does not match \
                            %s.%s.%s '
                            'signature' % (method, url, controller.__module__,
                                       controller.__name__, action))
            else:
                try:
                    mok('SELF', 'REQUEST', **m)
                except TypeError:
                    self.fail('Arguments in route "%s %s" does not match \
                            %s.%s.%s '
                            'signature' % (method, url, controller.__module__,
                                       controller.__name__, action))
