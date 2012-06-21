import unittest
import mock

from balancer.api.v1 import loadbalancers


class TestLoadBalancersController(unittest.TestCase):
    def setUp(self):
        super(TestLoadBalancersController, self).setUp()
        self.conf = mock.Mock()
        self.controller = loadbalancers.Controller(self.conf)
        self.req = mock.Mock()

    @mock.patch('balancer.core.api.lb_find_for_vm', autospec=True)
    def test_find_lb_for_vm(self, mock_lb_find_for_vm):
        mock_lb_find_for_vm.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id',
                            'X-Tenant-Name': 'fake_tenant_name'}
        resp = self.controller.findLBforVM(self.req, vm_id='123')
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.lb_get_index', autospec=True)
    def test_index(self, mock_lb_get_index):
        mock_lb_get_index.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.index(self.req)
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.create_lb', autospec=True)
    @mock.patch('balancer.db.api.loadbalancer_create', autospec=True)
    def test_create(self, mock_loadbalancer_create, mock_create_lb):
        mock_loadbalancer_create.return_value = {'id': '1'}
        mock_create_lb.return_value = {'id': '1'}
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.create(self.req, body={})
        self.assertEqual(resp, {'loadbalancers': {'id': 'foo'}})

    @mock.patch('balancer.core.api.delete_lb', autospec=True)
    def test_delete(self, mock_delete_lb):
        resp = self.controller.delete(self.req, id='123')
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_get_data', autospec=True)
    def test_show(self, mock_lb_get_data):
        mock_lb_get_data.return_value = 'foo'
        resp = self.controller.show(self.req, id='123')
        self.assertEqual(resp, {'loadbalancer': 'foo'})

    @mock.patch('balancer.core.api.lb_show_details', autospec=True)
    def test_show_details(self, mock_lb_show_details):
        mock_lb_show_details.return_value = 'foo'
        resp = self.controller.showDetails(self.req, id='123')
        self.assertEqual('foo', resp)

    @mock.patch('balancer.core.api.update_lb', autospec=True)
    def test_update(self, mock_update_lb):
        resp = self.controller.update(self.req, id='123', body='body')
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_add_node', autospec=True)
    def test_add_node(self, mock_lb_add_node):
        mock_lb_add_node.return_value = 'foo'
        resp = self.controller.addNode(self.req, id='123', body={'node': 'foo'})
        self.assertEqual(resp, 'foo')


    @mock.patch('balancer.core.api.lb_show_nodes', autospec=True)
    def test_show_nodes(self, mock_lb_show_nodes):
        mock_lb_show_nodes.return_value = 'foo'
        resp = self.controller.showNodes(self.req, id='123')
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_delete_node', autospec=True)
    def test_delete_node(self, mock_lb_delete_node):
        resp = self.controller.deleteNode(self.req, id='123', nodeID='321')
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_change_node_status', autospec=True)
    def test_change_node_status(self, mock_lb_change_node_status):
        req_kwargs = {'id': '1',
                      'nodeID': '1',
                      'status': 'FAKESTATUSA'}
        resp = self.controller.changeNodeStatus(self.req, **req_kwargs)
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_update_node', autospec=True)
    def test_update_node(self, mock_lb_update_node):
        req_kwargs = {'id': '1',
                      'nodeID': '1',
                      'body': {'node': 'node'}}
        resp = self.controller.updateNode(self.req, **req_kwargs)
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_show_probes', autospec=True)
    def test_show_monitoring(self, mock_lb_show_probes):
        mock_lb_show_probes.return_value = 'foo'
        resp = self.controller.showMonitoring(self.req, id='1')
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_add_probe', autospec=True)
    def test_add_probe(self, mock_lb_add_probe):
        mock_lb_add_probe.return_value = '1'
        req_kwargs = {'id': '1',
                      'body': {'healthMonitoring': {'probe': 'foo'}}}
        resp = self.controller.addProbe(self.req, **req_kwargs)
        self.assertEqual(resp, '1')

    @mock.patch('balancer.core.api.lb_delete_probe', autospec=True)
    def test_delete_probe(self, mock_lb_delete_probe):
        resp = self.controller.deleteProbe(self.req, id='1', probeID='1')
        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.core.api.lb_show_sticky', autospec=True)
    def test_show_stickiness(self, mock_lb_show_sticky):
        mock_lb_show_sticky.return_value = 'foo'
        resp = self.controller.showStickiness(self.req, id='1')
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_add_sticky', autospec=True)
    def test_add_sticky(self, mock_lb_add_sticky):
        mock_lb_add_sticky.return_value = '1'
        req_kwargs = {'id': '1',
                      'body': {'sessionPersistence': 'foo'}}
        resp = self.controller.addSticky(self.req, **req_kwargs)
        self.assertEqual(resp, '1')

    @mock.patch('balancer.core.api.lb_delete_sticky', autospec=True)
    def test_delete_sticky(self, mock_lb_delete_sticky):
        resp = self.controller.deleteSticky(self.req, id='1', stickyID='1')
        self.assertEqual(resp.status_int, 202)
