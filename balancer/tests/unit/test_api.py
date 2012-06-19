# vim: tabstop=4 shiftwidth=4 softtabstop=4

from mock import patch, MagicMock as Mock
from unittest import TestCase
#from balancer.core import commands
#from balancer.loadbalancers.vserver import Balancer
#from balancer.devices.DeviceMap import DeviceMap
#from balancer.core.scheduller import Scheduller
from balancer.storage.storage import Storage
import balancer.core.api as api


class WorkWithReader(TestCase):

    def setUp(self):
        self.conf = Mock()
        self.tenant_id = Mock()
        #self.tenant_id.return_value = "foo"
        self.store = Mock(spec=Storage(self.conf))
        #self.store.getReader = Mock()
        #self.reader = self.store.getReader()

    @patch("balancer.db.api.loadbalancer_get_all_by_project")
    def test_lb_get_index(self, mock_api):
        api.lb_get_index(self.conf, self.tenant_id)
        self.assertTrue(mock_api.called)

    @patch("balancer.db.api.loadbalancer_get_all_by_vm_id")
    def test_lb_find_for_vm(self, mock_api):
        vm_id = Mock()
        api.lb_find_for_vm(self.conf, vm_id, self.tenant_id)
        self.assertTrue(mock_api.called)

    @patch("balancer.db.api.loadbalancer_get")
    def test_get_data(self, mock_api):
        lb_id = Mock()
        lb_id.return_value = ""
        api.lb_get_data(self.conf, lb_id)
        self.assertTrue(mock_api.called)
#class WorkWithBalancer(TestCase):
