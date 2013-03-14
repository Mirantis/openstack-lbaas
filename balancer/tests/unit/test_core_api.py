import mock
import unittest
import types
import balancer.core.api as api
from openstack.common import exception
from balancer import exception as exc
import balancer.db.models as models


class TestDecorators(unittest.TestCase):

    def setUp(self):
        self.func = mock.MagicMock(__name__='Test func',
                return_value=mock.MagicMock(spec=types.FunctionType))

    def test_asynchronous_1(self):
        wrapped = api.asynchronous(self.func)
        wrapped(async=False)
        self.assertEquals(self.func.call_args_list, [mock.call()])

    @mock.patch("eventlet.spawn")
    def test_asynchronous_2(self, mock_event):
        wrapped = api.asynchronous(self.func)
        wrapped(async=True)
        self.assertTrue(mock_event.called)


class TestBalancer(unittest.TestCase):
    patch_balancer = mock.patch("balancer.loadbalancers.vserver.Balancer")
    patch_schedule = mock.patch("balancer.core.scheduler.schedule")
    patch_reschedule = mock.patch("balancer.core.scheduler.reschedule")
    patch_logger = mock.patch("logging.getLogger")

    def setUp(self):
        self.conf = mock.MagicMock()
        value = mock.MagicMock
        self.dict_list = [{'id': 1, 'name': 'name', 'extra': {
            'stragearg': value, 'anotherarg': value}, },
            {'id': 2, 'name': 'name0', 'extra': {
                'stragearg': value, 'anotherarg': value}, }]
        self.dictionary = {'id': 1, 'name': 'name', 'extra': {
            'stragearg': value, 'anotherarg': value}, }
        self.tenant_id = 1
        self.lb_id = 1
        self.lb_node = self.dictionary
        self.lb_nodes = self.dict_list
        self.lb_node_id = 1
        self.lb_body_0 = {'bubble': "bubble"}
        self.lb_body = {'algorithm': "bubble"}
        self.dict_list_0 = {'nodes': [{'id': 1, 'name': 'name',
            'extra': {'stragearg': value, 'anotherarg': value}}],
            'healthMonitor': [{'id': 2, 'name': 'name0', 'extra': {
                'stragearg': value, 'anotherarg': value}}],
            'virtualIps': [{'id': 333, 'name': 'name0', 'extra': {
                'stragearg': value, 'anotherarg': value}}]}

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.loadbalancer_get_all_by_project")
    def test_lb_get_index(self, mock_api, mock_extra):
        mock_api.return_value = [{'id': 1, 'virtualIps': 'foo'}, {'id': 2}]
        mock_extra.return_value = 'foo'
        resp = api.lb_get_index(self.conf, self.tenant_id)
        self.assertTrue(mock_api.called)
        self.assertTrue(mock_extra.called)
        self.assertTrue(mock_extra.call_count == 2)
        self.assertEqual(resp, ['foo', 'foo'])
        mock_api.assert_called_once_with(self.conf, self.tenant_id)
        mock_extra.assert_any_call({'id': 1, 'virtualIps': 'foo'})
        mock_extra.assert_any_call({'id': 2})

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.loadbalancer_get_all_by_vm_id")
    def test_lb_find_for_vm(self, mock_api, mock_extra):
        vm_id = mock.Mock()
        mock_api.return_value = ['foo']
        mock_extra.return_value = 'foo'
        resp = api.lb_find_for_vm(self.conf, 'fake_tenant', vm_id)
        mock_api.assert_called_once_with(self.conf, 'fake_tenant', vm_id)
        mock_extra.assert_called_once_with('foo')
        self.assertTrue(mock_api.called)
        self.assertEqual(resp, ['foo'])

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    def test_lb_show_details(self, *mocks):
        mocks[5].return_value = {"virtualIps": 1, "nodes": 2,
                "healthMonitor": 3, "sessionPersistence": 4}
        mocks[6].return_value = mock.MagicMock(spec=models.ServerFarm)
        api.lb_show_details(self.conf, 'fake_tenant', self.lb_id)
        for mok in mocks:
            self.assertTrue(mok.called, "This mock %s didn't call"
                    % mok._mock_name)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_get_data_0(self, mock_api, mock_bal):
        api.lb_get_data(self.conf, 'fake_tenant', self.lb_id)
        self.assertTrue(mock_api.called)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_get_data_1(self, mock_api, mock_bal):
        mock_api.return_value = {"id": 1, "virtualIps": "cranch"}
        res = api.lb_get_data(self.conf, 'fake_tenant', self.lb_id)
        self.assertTrue(mock_api.called)
        self.assertEquals(res, {"id": 1})

    @mock.patch("balancer.db.api.probe_create")
    @mock.patch("balancer.db.api.probe_pack_extra")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_pack_extra")
    @mock.patch("balancer.db.api.virtualserver_create")
    @mock.patch("balancer.db.api.virtualserver_pack_extra")
    @mock.patch("balancer.db.api.serverfarm_create")
    @mock.patch("balancer.db.api.predictor_create")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.loadbalancer_create")
    @mock.patch("balancer.db.api.loadbalancer_pack_extra")
    @patch_schedule
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_0(self, *mocks):
        """No exception"""
        mocks[2].return_value = {'id': 1}
        mocks[4].return_value = {'id': 2, 'algorithm': 'test',
                                 'protocol': 'test'}
        api.create_lb(self.conf, self.dict_list_0)
        for mok in mocks:
            self.assertTrue(mok.called, "Mock %s didn't call"
                    % mok._mock_name)
        mocks[5].assert_called_with(self.conf, 2,
                                    {'status': 'ACTIVE', 'deployed': True})

    @mock.patch("balancer.db.api.probe_create")
    @mock.patch("balancer.db.api.probe_pack_extra")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_pack_extra")
    @mock.patch("balancer.db.api.virtualserver_create")
    @mock.patch("balancer.db.api.virtualserver_pack_extra")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.loadbalancer_create")
    @mock.patch("balancer.db.api.loadbalancer_pack_extra")
    @mock.patch("balancer.db.api.serverfarm_create")
    @mock.patch("balancer.db.api.predictor_create")
    @patch_schedule
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_create_lb_1(self, *mocks):
        """Exception"""
        mocks[6].return_value = {'id': 2, 'algorithm': 'test',
                                 'protocol': 'test'}
        mocks[1].side_effect = exception.Invalid
        mocks[2].return_value = {'id': 1}
        mocks[4].return_value = mock.MagicMock()
        self.assertRaises(exception.Invalid, api.create_lb,
                          self.conf, self.dict_list_0)
        mocks[7].assert_called_with(self.conf, 2,
                                    {'status': 'ERROR', 'deployed': False})

    @patch_reschedule
    @mock.patch("balancer.core.commands.delete_loadbalancer")
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.predictor_get_by_sf_id")
    @mock.patch("balancer.db.api.predictor_update")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_update")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_update_lb(self,
                       mock_get_device_driver,
                       mock_sticky_get_all_by_sf_id,
                       mock_probe_get_all_by_sf_id,
                       mock_server_get_all_by_sf_id,
                       mock_virtualserver_update,
                       mock_virtualserver_get_all_by_sf_id,
                       mock_predictor_update,
                       mock_predictor_get_by_sf_id,
                       mock_serverfarm_get_all_by_lb_id,
                       mock_loadbalancer_update,
                       mock_loadbalancer_get,
                       mock_create_loadbalancer,
                       mock_delete_loadbalancer,
                       mock_reschedule):
        lb_body = {'algorithm': 'FAKE_ALGO1', 'protocol': 'FAKE_PROTO1'}
        mock_loadbalancer_get.return_value = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakename',
            'algorithm': 'FAKE_ALGO0',
            'protocol': 'FAKE_PROTO0',
        }
        mock_loadbalancer_update.return_value = lb_ref = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakename',
            'algorithm': 'FAKE_ALGO1',
            'protocol': 'FAKE_PROTO1',
        }
        mock_reschedule.return_value = {'id': 'fakedeviceid'}
        sf_ref = {'id': 'fakesfid'}
        mock_serverfarm_get_all_by_lb_id.return_value = [sf_ref]
        predictor_ref = {'id': 'fakepredid'}
        mock_predictor_get_by_sf_id.return_value = predictor_ref
        vip_ref = {'id': 'fakevipid', 'extra': {'protocol': 'FAKE_PROTO0'}}
        mock_virtualserver_get_all_by_sf_id.return_value = [vip_ref]
        mock_servers = mock_server_get_all_by_sf_id.return_value
        mock_probes = mock_probe_get_all_by_sf_id.return_value
        mock_stickies = mock_sticky_get_all_by_sf_id.return_value
        mock_device_driver = mock_get_device_driver.return_value
        api.update_lb(self.conf, 'faketenantid', self.lb_id, lb_body,
                      async=False)
        mock_loadbalancer_get.assert_called_once_with(self.conf, self.lb_id,
                                                      tenant_id='faketenantid')
        mock_serverfarm_get_all_by_lb_id.assert_called_once_with(self.conf,
                                                                 self.lb_id)
        mock_predictor_get_by_sf_id.assert_called_once_with(self.conf,
                                                            sf_ref['id'])
        mock_predictor_update.assert_called_once_with(self.conf,
            predictor_ref['id'], {'type': 'FAKE_ALGO1'})
        mock_virtualserver_get_all_by_sf_id.assert_called_once_with(self.conf,
                                                            sf_ref['id'])
        mock_virtualserver_update.assert_called_once_with(self.conf,
            vip_ref['id'], {'id': 'fakevipid',
                            'extra': {'protocol': 'FAKE_PROTO1'}})
        for mock_func in [mock_server_get_all_by_sf_id,
                          mock_probe_get_all_by_sf_id,
                          mock_sticky_get_all_by_sf_id]:
            mock_func.assert_called_once_with(self.conf, sf_ref['id'])
        mock_get_device_driver.assert_called_once_with(self.conf,
                                                       lb_ref['device_id'])
        mock_loadbalancer_update.assert_has_calls([
            mock.call(self.conf, self.lb_id, lb_ref),
            mock.call(self.conf, self.lb_id, {'status': 'ACTIVE'}),
        ])

        # reschedule returns another device
        mock_reschedule.return_value = {'id': 'anotherdeviceid'}
        mock_loadbalancer_update.reset_mock()
        mock_loadbalancer_get.return_value['algorithm'] = 'FAKE_ALGO0'
        api.update_lb(self.conf, 'faketenantid', self.lb_id, lb_body,
                      async=False)
        mock_loadbalancer_update.assert_has_calls([
            mock.call(self.conf, self.lb_id, lb_ref),
            mock.call(self.conf, self.lb_id, {'device_id': 'anotherdeviceid'}),
            mock.call(self.conf, self.lb_id, {'status': 'ACTIVE'}),
        ])

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.predictor_update")
    @mock.patch("balancer.db.api.predictor_get_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.loadbalancer_get")
    def test_update_lb_nothing(self,
                               mock_loadbalancer_get,
                               mock_loadbalancer_update,
                               *mock_funcs):
        lb_body = {'name': 'fakenewname'}
        mock_loadbalancer_get.return_value = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakename',
            'algorithm': 'FAKE_ALGO0',
            'protocol': 'FAKE_PROTO0',
        }
        mock_loadbalancer_update.return_value = lb_ref = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakenewname',
            'algorithm': 'FAKE_ALGO0',
            'protocol': 'FAKE_PROTO0',
        }
        sf_ref = {'id': 'fakesfid'}
        api.update_lb(self.conf, 'faketenantid', self.lb_id, lb_body,
                      async=False)
        mock_loadbalancer_get.assert_called_once_with(self.conf, self.lb_id,
                                                      tenant_id='faketenantid')
        for mock_func in mock_funcs:
            mock_func.assert_has_calls([])

    @patch_reschedule
    @mock.patch("balancer.core.commands.delete_loadbalancer")
    @mock.patch("balancer.core.commands.create_loadbalancer")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.loadbalancer_update")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.predictor_get_by_sf_id")
    @mock.patch("balancer.db.api.predictor_update")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.drivers.get_device_driver")
    def test_update_lb_error(self,
                             mock_get_device_driver,
                             mock_sticky_get_all_by_sf_id,
                             mock_probe_get_all_by_sf_id,
                             mock_server_get_all_by_sf_id,
                             mock_virtualserver_get_all_by_sf_id,
                             mock_predictor_update,
                             mock_predictor_get_by_sf_id,
                             mock_serverfarm_get_all_by_lb_id,
                             mock_loadbalancer_update,
                             mock_loadbalancer_get,
                             mock_create_loadbalancer,
                             mock_delete_loadbalancer,
                             mock_reschedule):
        lb_body = {'algorithm': 'FAKE_ALGO1'}
        mock_loadbalancer_get.return_value = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakename',
            'algorithm': 'FAKE_ALGO0',
            'protocol': 'FAKE_PROTO0',
        }
        mock_loadbalancer_update.return_value = lb_ref = {
            'id': self.lb_id,
            'device_id': 'fakedeviceid',
            'name': 'fakename',
            'algorithm': 'FAKE_ALGO1',
            'protocol': 'FAKE_PROTO0',
        }
        mock_reschedule.return_value = {'id': 'fakedeviceid'}
        sf_ref = {'id': 'fakesfid'}
        mock_serverfarm_get_all_by_lb_id.return_value = [sf_ref]
        predictor_ref = {'id': 'fakepredid'}
        mock_predictor_get_by_sf_id.return_value = predictor_ref

        # assume core.commands.delete_loadbalancer raises error
        mock_delete_loadbalancer.side_effect = exception.Invalid
        self.assertRaises(exception.Invalid, api.update_lb, self.conf,
                          'faketenantid', self.lb_id, lb_body, async=False)
        mock_loadbalancer_update.assert_has_calls([
            mock.call(self.conf, self.lb_id, lb_ref),
            mock.call(self.conf, self.lb_id, {'status': 'ERROR'}), ])

        # assume core.commands.create_loadbalancer raises error
        mock_delete_loadbalancer.side_effect = None
        mock_loadbalancer_update.reset_mock()
        mock_loadbalancer_get.return_value['algorithm'] = 'FAKE_ALGO0'
        mock_create_loadbalancer.side_effect = exception.Invalid
        self.assertRaises(exception.Invalid, api.update_lb, self.conf,
                          'faketenantid', self.lb_id, lb_body, async=False)
        mock_loadbalancer_update.assert_has_calls([
            mock.call(self.conf, self.lb_id, lb_ref),
            mock.call(self.conf, self.lb_id, {'status': 'ERROR'}), ])

    @mock.patch("balancer.db.api.virtualserver_destroy_by_sf_id")
    @mock.patch("balancer.db.api.predictor_destroy_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_destroy")
    @mock.patch("balancer.db.api.loadbalancer_destroy")
    @mock.patch("balancer.db.api.server_destroy_by_sf_id")
    @mock.patch("balancer.db.api.sticky_destroy_by_sf_id")
    @mock.patch("balancer.db.api.probe_destroy_by_sf_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.virtualserver_get_all_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.delete_loadbalancer")
    def test_delete_lb(self, *mocks):
        mocks[2].return_value = mock.MagicMock()
        api.delete_lb(self.conf, 'fake_tenant', self.lb_id)
        for m in mocks:
            self.assertTrue(m.called, "Mock %s wasn't called"
                    % m._mock_name)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_pack_extra")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_node_to_loadbalancer")
    def test_lb_add_nodes(self, *mocks):
        mocks[2].return_value = {'device_id': 1}
        mocks[3].return_value = [{'id': 1}]
        api.lb_add_nodes(self.conf, 'fake_tenant', self.lb_id, self.lb_nodes)
        for mok in mocks:
            self.assertTrue(mok.called, "This mock didn't call %s"
                    % mok._mock_name)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.server_get_all_by_sf_id")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    def test_lb_show_nodes(self, mock_serverfarm, mock_server, mock_unpack):
        mock_serverfarm.return_value = self.dict_list
        api.lb_show_nodes(self.conf, 'fake_tenant', 1)
        self.assertTrue(mock_serverfarm.called)
        self.assertTrue(mock_server.called)

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.remove_node_from_loadbalancer")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.server_destroy")
    def test_lb_delete_node(self, *mocks):
        mocks[5].return_value = self.dict_list
        api.lb_delete_node(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.activate_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_0(self, *mocks):
        """Activate server called"""
        lb_node_status = "inservice"
        api.lb_change_node_status(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id, lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.suspend_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_1(self, *mocks):
        """Suspend server called"""
        lb_node_status = ""
        api.lb_change_node_status(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id, lb_node_status)
        for mock in mocks:
            self.assertTrue(mock.called)

    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.activate_rserver")
    @mock.patch("balancer.core.commands.suspend_rserver")
    @mock.patch("balancer.db.api.server_get")
    def test_lb_change_node_status_2(self, *mocks):
        """return ok"""
        mocks[0].return_value = {'sf_id': 1, 'state': 'status'}
        api.lb_change_node_status(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id, 'status')
        self.assertFalse(mocks[1].called)
        self.assertFalse(mocks[2].called)

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.server_create")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.server_destroy")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    def test_lb_update_node_0(self, mock_com0, mock_com1, *mocks):
        """"""
        api.lb_update_node(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id, self.lb_node)
        self.assertTrue(mock_com0.called)
        self.assertTrue(mock_com1.called)

    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.server_update")
    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get")
    @mock.patch("balancer.core.commands.delete_rserver_from_server_farm")
    @mock.patch("balancer.core.commands.add_rserver_to_server_farm")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_update_node(self, mock_extra, mock_command1, mock_command2,
                            mock_sf, mock_lb, mock_get, mock_update,
                            mock_driver):
        """"""
        mock_extra.return_value = self.dictionary
        mock_lb.return_value.__getitem__.return_value = 2
        resp = api.lb_update_node(self.conf,
                'fake_tenant', self.lb_id, self.lb_node_id, self.lb_node)
        self.assertEqual(resp, self.dictionary)
        mock_update.assert_called_once_with(self.conf,
                                            mock_get.return_value['id'],
                                            mock_get.return_value)
        mock_extra.assert_called_once_with(mock_update.return_value)
        mock_get.assert_called_once_with(self.conf,
                self.lb_node_id, tenant_id='fake_tenant')
        mock_sf.assert_called_once_with(self.conf,
                                        mock_get.return_value['sf_id'])
        mock_lb.assert_called_once_with(self.conf, self.lb_id)
        mock_driver.assert_called_once_with(self.conf, 2)
        with mock_driver.return_value.request_context() as ctx:
            mock_command1.assert_called_once_with(ctx, mock_sf.return_value,
                                                  mock_update.return_value)
            mock_command2.assert_called_once_with(ctx, mock_sf.return_value,
                                                  mock_get.return_value)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    def test_lb_show_probes_0(self, db_api0, db_api1, db_api2):
        db_api0.return_value = self.dict_list
        db_api1.return_value.__getitem__.return_value.\
                             __getitem__.return_value = 2
        db_api2.return_value = {'probe': 'foo'}
        resp = api.lb_show_probes(self.conf, 'fake_tenant', self.lb_id)
        self.assertTrue(db_api1.called)
        self.assertTrue(db_api2.called)
        self.assertTrue(db_api2.call_count == 2)
        self.assertEqual(resp, {'healthMonitoring': [{'probe': 'foo'},
                                                     {'probe': 'foo'}]})
        db_api0.assert_called_once_with(self.conf, 2)
        db_api1.assert_called_once_with(self.conf,
                self.lb_id, tenant_id='fake_tenant')
        db_api2.assert_any_call(self.dict_list[0])
        db_api2.assert_any_call(self.dict_list[1])

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_get_all_by_sf_id")
    def test_lb_show_probes_1(self, db_api0, db_api1, db_api2):
        db_api1.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_show_probes(self.conf, 'fake_tenant', self.lb_id)
            self.assertFalse(db_api0.called)
            self.assertFalse(db_api2.called)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_pack_extra")
    @mock.patch("balancer.db.api.probe_create")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_probe_to_loadbalancer")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_add_probe_0(self, mock_unpack, mock_command, mock_driver,
                            mock_create, mock_pack, mock_sf, mock_lb):
        """lb_probe['type']!=None"""
        lb_probe = {'type': 'Gvido'}
        mock_sf.return_value.__getitem__.return_value = {'id': 'foo'}
        mock_unpack.return_value = self.dictionary
        resp = api.lb_add_probe(self.conf, 'fake_tenant', self.lb_id, lb_probe)
        self.assertEqual(resp, self.dictionary)
        mock_unpack.assert_called_once_with(mock_create.return_value)
        mock_pack.assert_called_once_with(lb_probe)
        mock_create.assert_called_once_with(self.conf, mock_pack.return_value)
        mock_sf.assert_called_once_with(self.conf, mock_lb.return_value['id'])
        mock_lb.assert_called_once_with(self.conf,
                self.lb_id, tenant_id='fake_tenant')
        with mock_driver.return_value.request_context() as ctx:
            mock_command.assert_called_once_with(ctx, {'id': 'foo'},
                                                 mock_create.return_value)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_pack_extra")
    @mock.patch("balancer.db.api.probe_create")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_probe_to_loadbalancer")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_add_probe_1(self, *mocks):
        """lb_probe['type']=None"""
        lb_probe = {'type': None}
        resp = api.lb_add_probe(self.conf, 'fake_tenant', self.lb_id, lb_probe)
        self.assertEqual(resp, None)
        for mock in mocks:
            self.assertFalse(mock.called)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    def test_lb_add_probe_2(self, mock_sf, mock_lb):
        """Exception"""
        lb_probe = {'type': 'Gvido'}
        mock_sf.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_add_probe(self.conf, 'fake_tenant', self.lb_id, lb_probe)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.probe_pack_extra")
    @mock.patch("balancer.db.api.probe_create")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_probe_to_loadbalancer")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_add_probe_2(self, *mocks):
        """lb_probe['type']!=None"""
        lb_probe = {'type': 'Gvido'}
        mocks[5].side_effect = IndexError
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_add_probe(self.conf, 'fake_tenant', self.lb_id, lb_probe)
   #     for mok in mocks:
   #         self.assertTrue(mok.called)

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.db.api.probe_get")
    @mock.patch("balancer.db.api.probe_destroy")
    @mock.patch("balancer.core.commands.remove_probe_from_server_farm")
    def test_lb_delete_probe(self, *mocks):
        mocks[5].return_value = self.dict_list
        api.lb_delete_probe(self.conf, 'fake_tenant', self.lb_id, self.lb_id)
        for mok in mocks:
            self.assertTrue(mok.called)

    @mock.patch("balancer.core.scheduler.reschedule", autospec=True)
    @mock.patch("balancer.db.api.unpack_extra", autospec=True)
    @mock.patch("balancer.core.commands.create_vip", autospec=True)
    @mock.patch("balancer.drivers.get_device_driver", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_create", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_pack_extra", autospec=True)
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id", autospec=True)
    @mock.patch("balancer.db.api.loadbalancer_get", autospec=True)
    def test_lb_add_vip(self,
                        mock_loadbalancer_get,
                        mock_serverfarm_get_all_by_lb_id,
                        mock_virtualserver_pack_extra,
                        mock_virtualserver_create,
                        mock_get_device_driver,
                        mock_create_vip,
                        mock_unpack_extra,
                        mock_reschedule):
        # Mock
        lb_ref = {
            'id': 'fakelbid',
            'device_id': 'fakedeviceid',
            'protocol': 'HTTP',
        }
        mock_loadbalancer_get.return_value = lb_ref
        sf_ref = mock.MagicMock()
        sf_ref.__getitem__.return_value = 'fakesfid'
        mock_serverfarm_get_all_by_lb_id.return_value = [sf_ref]
        mock_virtualserver_pack_extra.return_value = {}
        mock_virtualserver_create.return_value = vip_ref = mock.Mock()
        ctx = mock.MagicMock()
        ctx.__enter__.return_value = enter_ctx = mock.Mock()
        mock_get_device_driver.return_value = \
            mock.Mock(request_context=mock.Mock(return_value=ctx))
        mock_reschedule.return_value = {'id': lb_ref['device_id']}
        # Call
        api.lb_add_vip(self.conf, 'fake_tenant', 'fakelbid', 'fakevipdict')
        # Assert
        mock_loadbalancer_get.assert_called_once_with(self.conf,
                'fakelbid', tenant_id='fake_tenant')
        mock_serverfarm_get_all_by_lb_id.assert_called_once_with(self.conf,
                                                                 'fakelbid')
        mock_virtualserver_pack_extra.assert_called_once_with('fakevipdict')
        mock_virtualserver_create.assert_called_once_with(self.conf, {
            'lb_id': 'fakelbid',
            'sf_id': 'fakesfid',
            'extra': {
                'protocol': 'HTTP',
            },
        })
        mock_get_device_driver.assert_called_once_with(self.conf,
                                                       'fakedeviceid')
        mock_create_vip.assert_called_once_with(enter_ctx, vip_ref, sf_ref)
        mock_unpack_extra.assert_called_once_with(vip_ref)

    @mock.patch("balancer.db.api.unpack_extra", autospec=True)
    @mock.patch("balancer.core.commands.create_vip", autospec=True)
    @mock.patch("balancer.drivers.get_device_driver", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_create", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_pack_extra", autospec=True)
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id", autospec=True)
    @mock.patch("balancer.db.api.loadbalancer_get", autospec=True)
    def test_lb_add_vip_failed(self,
                               mock_loadbalancer_get,
                               mock_serverfarm_get_all_by_lb_id,
                               mock_virtualserver_pack_extra,
                               mock_virtualserver_create,
                               mock_get_device_driver,
                               mock_create_vip,
                               mock_unpack_extra):
        mock_serverfarm_get_all_by_lb_id.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_add_vip(self.conf, 'fake_tenant', 'fakelbid', 'fakevipdict')
        self.assertTrue(mock_loadbalancer_get.called)
        self.assertTrue(mock_serverfarm_get_all_by_lb_id.called)
        self.assertFalse(mock_virtualserver_pack_extra.called)
        self.assertFalse(mock_virtualserver_create.called)
        self.assertFalse(mock_get_device_driver.called)
        self.assertFalse(mock_create_vip.called)
        self.assertFalse(mock_unpack_extra.called)

    @mock.patch("balancer.core.commands.delete_vip", autospec=True)
    @mock.patch("balancer.drivers.get_device_driver", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_destroy", autospec=True)
    @mock.patch("balancer.db.api.virtualserver_get", autospec=True)
    @mock.patch("balancer.db.api.loadbalancer_get", autospec=True)
    def test_lb_delete_vip(self,
                           mock_loadbalancer_get,
                           mock_virtualserver_get,
                           mock_virtualserver_destroy,
                           mock_get_device_driver,
                           mock_delete_vip):
        # Mock
        mock_loadbalancer_get.return_value = lb_ref = mock.MagicMock()
        lb_ref.__getitem__.return_value = 'fakedeviceid'
        mock_virtualserver_get.return_value = vip_ref = mock.Mock()
        ctx = mock.MagicMock()
        ctx.__enter__.return_value = enter_ctx = mock.Mock()
        mock_get_device_driver.return_value = \
            mock.Mock(request_context=mock.Mock(return_value=ctx))
        # Call
        api.lb_delete_vip(self.conf, 'fake_tenant', 'fakelbid', 'fakevipid')
        # Assert
        mock_loadbalancer_get.assert_called_once_with(self.conf,
                'fakelbid', tenant_id='fake_tenant')
        mock_virtualserver_get.assert_called_once_with(self.conf, 'fakevipid')
        mock_virtualserver_destroy.assert_called_once_with(self.conf,
                                                           'fakevipid')
        mock_get_device_driver.assert_called_once_with(self.conf,
                                                       'fakedeviceid')
        mock_delete_vip.assert_called_once_with(enter_ctx, vip_ref)

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_sticky0(self, db_api0, db_api1, db_api2):
        db_api0.return_value = {'sticky': 'foo'}
        db_api1.return_value = self.dict_list
        db_api2.return_value.__getitem__.return_value.\
                             __getitem__.return_value = 2
        resp = api.lb_show_sticky(self.conf, 'fake_tenant', self.lb_id)
        self.assertEqual(resp, {"sessionPersistence": [{'sticky': 'foo'},
                                                       {'sticky': 'foo'}]})
        self.assertTrue(db_api0.called)
        self.assertTrue(db_api0.call_count == 2)
        self.assertTrue(db_api1.called)
        self.assertTrue(db_api2.called)
        db_api0.assert_any_call(self.dict_list[0])
        db_api0.assert_any_call(self.dict_list[1])
        db_api1.assert_called_once_with(self.conf, 2)
        db_api2.assert_called_once_with(self.conf,
                self.lb_id, tenant_id='fake_tenant')

    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.sticky_get_all_by_sf_id")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_lb_show_sticky1(self, db_api0, db_api1, db_api2):
        db_api2.return_value = []
        with self.assertRaises(exc.ServerFarmNotFound):
            api.lb_show_sticky(self.conf, 'fake_tenant', self.lb_id)
            self.assertFalse(db_api0.called)
            self.assertFalse(db_api1.called)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.sticky_create")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.sticky_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_sticky_to_loadbalancer")
    def test_lb_add_sticky0(self, *mocks):
        mocks[4].return_value = self.dict_list
        sticky = mock.MagicMock()
        api.lb_add_sticky(self.conf, 'fake_tenant', self.lb_id, sticky)
        for mok in mocks:
            self.assertTrue(mok.called)

    @mock.patch("balancer.db.api.unpack_extra")
    @mock.patch("balancer.db.api.sticky_create")
    @mock.patch("balancer.db.api.serverfarm_get_all_by_lb_id")
    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.sticky_pack_extra")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.add_sticky_to_loadbalancer")
    def test_lb_add_sticky1(self, *mocks):
        sticky = {'type': None}
        resp = api.lb_add_sticky(self.conf, 'fake_tenant', self.lb_id, sticky)
        self.assertEqual(resp, None)
        for mock in mocks:
            self.assertFalse(mock.called)

    @mock.patch("balancer.db.api.loadbalancer_get")
    @mock.patch("balancer.db.api.sticky_get")
    @mock.patch("balancer.db.api.sticky_destroy")
    @mock.patch("balancer.drivers.get_device_driver")
    @mock.patch("balancer.core.commands.remove_sticky_from_loadbalancer")
    def test_lb_delete_sticky(self, mock_command, mock_driver, mock_destroy,
                              mock_get, mock_bal):
        mock_bal.return_value = {'id': 2, 'device_id': 2}
        resp = api.lb_delete_sticky(self.conf, 'fake_tenant', self.lb_id, 1)
        self.assertEqual(resp, 1)
        mock_bal.assert_called_once_with(self.conf,
                self.lb_id, tenant_id='fake_tenant')
        mock_get.assert_called_once_with(self.conf, 1)
        mock_destroy.assert_called_once_with(self.conf, 1)
        mock_driver.assert_called_once_with(self.conf, 2)
        with mock_driver.return_value.request_context() as ctx:
            mock_command.assert_called_once_with(ctx, mock_bal.return_value,
                                                 mock_get.return_value)


class TestDevice(unittest.TestCase):
    def setUp(self):
        self.conf = mock.MagicMock(register_group=mock.MagicMock)
        self.dict_list = ({'id': 1}, {'id': 2},)

    @mock.patch("balancer.db.api.device_get_all")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_device_get_index(self, mock_f1, mock_f2):
        mock_f1.side_effect = [{'device': 1}, {'device': 2}]
        mock_f2.return_value = [[{'id': 1}], [{'id': 2}]]
        resp = api.device_get_index(self.conf)
        self.assertEqual(resp, [{'device': 1}, {'device': 2}])
        self.assertTrue(mock_f1.called)
        self.assertTrue(mock_f2.called)
        mock_f1.assert_any_call([{'id': 1}])
        mock_f1.assert_any_call([{'id': 2}])
        mock_f2.assert_called_once_with(self.conf)

    @mock.patch("balancer.db.api.device_pack_extra")
    @mock.patch("balancer.db.api.device_create")
    def test_device_create(self,  mock_f1, mock_f2):
        mock_f1.return_value = {'id': 1}
        resp = api.device_create(self.conf)
        self.assertEqual(resp['id'], 1)
        self.assertTrue(mock_f1.called, "device_create not called")
        self.assertTrue(mock_f2.called, "device_pack_extra not called")
        mock_f1.assert_caleld_once_with(self.conf, mock_f2.return_value)
        mock_f2.assert_called_once_with({})

    def test_device_info(self):
        params = {'query_params': 2}
        res = api.device_info(params)
        self.assertEquals(res, None, "Alyarma!")

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_device_show_algorithms_0(self, mock_driver, mock_db_api):
        """capabilities = None"""
        mock_driver.get_capabilities = None
        mock_db_api.return_value = self.dict_list
        resp = api.device_show_algorithms(self.conf)
        self.assertEqual(resp, [])

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_device_show_algorithms_1(self, mock_driver, mock_db_api):
        """capabilities is not empty, not None"""
        mock_db_api.return_value = self.dict_list
        mock_driver.return_value = drv = mock.MagicMock()
        drv.get_capabilities.return_value = {"algorithms": ["CRYSIS"]}
        resp = api.device_show_algorithms(self.conf)
        self.assertEqual(resp, ["CRYSIS"])

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_device_show_algorithms_2(self, mock_driver, mock_db_api):
        """capabilities is empty"""
        mock_db_api.return_value = self.dict_list
        mock_driver.return_value = drv = mock.MagicMock()
        drv.get_capabilities.return_value = {}
        resp = api.device_show_algorithms(self.conf)
        self.assertEqual(resp, [])

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_show_protocols_0(self, mock_driver, mock_db_api):
        """capabilities = None"""
        mock_driver.get_capabilities = None
        mock_db_api.return_value = self.dict_list
        resp = api.device_show_protocols(self.conf)
        self.assertEqual(resp, [])

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_show_protocols_1(self, mock_driver, mock_db_api):
        """capabilities"""
        mock_db_api.return_value = self.dict_list
        mock_driver.return_value = drv = mock.MagicMock()
        drv.get_capabilities.return_value = {"protocols": ["CRYSIS"]}
        resp = api.device_show_protocols(self.conf)
        self.assertEqual(resp, ["CRYSIS"])

    @mock.patch('balancer.db.api.device_get_all')
    @mock.patch('balancer.drivers.get_device_driver')
    def test_show_protocols_2(self, mock_driver, mock_db_api):
        """capabilities"""
        mock_db_api.return_value = self.dict_list
        mock_driver.return_value = drv = mock.MagicMock()
        drv.get_capabilities.return_value = {}
        resp = api.device_show_protocols(self.conf)
        self.assertEqual(resp, [])
