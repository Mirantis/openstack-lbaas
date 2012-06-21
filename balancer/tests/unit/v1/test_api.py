import unittest
import mock

from balancer.api.v1 import loadbalancers


class TestLoadBalancersController(unittest.TestCase):
    def setUp(self):
        super(TestLoadBalancersController, self).setUp()
        self.conf = mock.Mock()
        self.controller = loadbalancers.Controller(self.conf)
        self.req = mock.Mock()

    def test_find_lb_for_vm(self):
        def lb_find_for_vm(conf, vm_id, tenant_id=''):
            return 'foo'

        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id',
                            'X-Tenant-Name': 'fake_tenant_name'}
        with mock.patch('balancer.core.api.lb_find_for_vm', lb_find_for_vm):
            resp = self.controller.findLBforVM(self.req, vm_id='123')
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    def test_index(self):
        def lb_get_index(conf, tenant_id=''):
            return 'foo'

        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        with mock.patch('balancer.core.api.lb_get_index', lb_get_index):
            resp = self.controller.index(self.req)
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    def test_create(self):
        def loadbalancer_create(conf, values):
            lb = values.copy()
            lb['id'] = 'foo'
            return lb

        def create_lb(conf, **params):
            lb = params['lb']
            return lb['id']

        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        with mock.patch('balancer.db.api.loadbalancer_create',
                        loadbalancer_create):
            with mock.patch('balancer.core.api.create_lb', create_lb):
                resp = self.controller.create(self.req, body={})
        self.assertEqual(resp, {'loadbalancers': {'id': 'foo'}})

    def test_delete(self):
        def delete_lb(conf, lb_id):
            return

        with mock.patch('balancer.core.api.delete_lb', delete_lb):
            resp = self.controller.delete(self.req, id='123')
        self.assertEqual(resp.status_int, 202)

    def test_show(self):
        def lb_get_data(conf, lb_id):
            return 'foo'

        with mock.patch('balancer.core.api.lb_get_data', lb_get_data):
            resp = self.controller.show(self.req, id='123')
        self.assertEqual(resp, {'loadbalancer': 'foo'})

    def test_show_details(self):
        def lb_show_details(conf, lb_id):
            return 'foo'

        with mock.patch('balancer.core.api.lb_show_details', lb_show_details):
            resp = self.controller.showDetails(self.req, id='123')
        self.assertEqual('foo', resp)

    def test_update(self):
        def update_lb(conf, lb_id, lb_body):
            pass

        with mock.patch('balancer.core.api.update_lb', update_lb):
            resp = self.controller.update(self.req, id='123', body='body')
        self.assertEqual(resp.status_int, 202)

    def test_add_node(self):
        def lb_add_node(conf, lb_id, lb_node):
            return 'foo'

        with mock.patch('balancer.core.api.lb_add_node', lb_add_node):
            resp = self.controller.addNode(self.req, id='123', body={'node': 'foo'})
        self.assertEqual(resp, 'foo')

    def test_show_nodes(self):
        def lb_show_nodes(conf, lb_id):
            return 'foo'

        with mock.patch('balancer.core.api.lb_show_nodes', lb_show_nodes):
            resp = self.controller.showNodes(self.req, id='123')
        self.assertEqual(resp, 'foo')

    def test_delete_node(self):
        def lb_delete_node(conf, lb_id, lb_node_id):
            return

        with mock.patch('balancer.core.api.lb_delete_node', lb_delete_node):
            resp = self.controller.deleteNode(self.req, id='123', nodeID='321')
        self.assertEqual(resp.status_int, 202)

    def test_change_node_status(self):
        def lb_change_node_status(conf, lb_id, lb_node_id, lb_node_status):
            pass

        req_kwargs = {'id': '1',
                      'nodeID': '1',
                      'status': 'FAKESTATUSA'}
        with mock.patch('balancer.core.api.lb_change_node_status', lb_change_node_status):
            resp = self.controller.changeNodeStatus(self.req, **req_kwargs)
        self.assertEqual(resp.status_int, 202)

    def test_update_node(self):
        def lb_update_node(conf, lb_id, lb_node_id, lb_node):
            pass

        req_kwargs = {'id': '1',
                      'nodeID': '1',
                      'body': {'node': 'node'}}
        with mock.patch('balancer.core.api.lb_update_node', lb_update_node):
            resp = self.controller.updateNode(self.req, **req_kwargs)
        self.assertEqual(resp.status_int, 202)

    def test_show_monitoring(self):
        def lb_show_probes(conf, lb_id):
            return 'foo'

        with mock.patch('balancer.core.api.lb_show_probes', lb_show_probes):
            resp = self.controller.showMonitoring(self.req, id='1')
        self.assertEqual(resp, 'foo')

    def test_add_probe(self):
        def lb_add_probe(conf, lb_id, lb_probe):
            return '1'

        req_kwargs = {'id': '1',
                      'body': {'healthMonitoring': {'probe': 'foo'}}}
        with mock.patch('balancer.core.api.lb_add_probe', lb_add_probe):
            resp = self.controller.addProbe(self.req, **req_kwargs)
        self.assertEqual(resp, '1')

    def test_delete_probe(self):
        def lb_delete_probe(conf, lb_id, probe_id):
            pass

        with mock.patch('balancer.core.api.lb_delete_probe', lb_delete_probe):
            resp = self.controller.deleteProbe(self.req, id='1', probeID='1')
        self.assertEqual(resp.status_int, 202)

    def test_show_stickiness(self):
        def lb_show_sticky(conf, lb_id):
            return 'foo'

        with mock.patch('balancer.core.api.lb_show_sticky', lb_show_sticky):
            resp = self.controller.showStickiness(self.req, id='1')
        self.assertEqual(resp, 'foo')

    def test_add_sticky(self):
        def lb_add_sticky(conf, lb_id, sticky):
            return '1'

        req_kwargs = {'id': '1',
                      'body': {'sessionPersistence': 'foo'}}
        with mock.patch('balancer.core.api.lb_add_sticky', lb_add_sticky):
            resp = self.controller.addSticky(self.req, **req_kwargs)
        self.assertEqual(resp, '1')

    def test_delete_sticky(self):
        def lb_delete_sticky(conf, lb_id, sticky_id):
            pass

        with mock.patch('balancer.core.api.lb_delete_sticky', lb_delete_sticky):
            resp = self.controller.deleteSticky(self.req, id='1', stickyID='1')
        self.assertEqual(resp.status_int, 202)
