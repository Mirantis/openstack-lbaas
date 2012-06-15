# vim: tabstop=4 shiftwidth=4 softtabstop=4

from mock import Mock
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
        self.tenant_id.return_value = "foo"
        self.store = Storage(self.conf)
        self.store.getReader = Mock()
        self.reader = self.store.getReader()

    def test_lb_get_index(self):
        res = api.lb_get_index(self.conf, self.tenant_id)
        self.assertEquals(res, "foo", "Something goes wrong")
        self.assertTrue(api.lb_get_index.called)

    def test_lb_find_for_vm(self):
        vm_id = Mock()
        res = api.lb_find_for_vm(self.conf, vm_id, self.tenant_id)
        self.assertTrue(api.lb_find_for_vm.called, "method didn't call")
        self.asserEquals(res, "foo", "Something goes wrong")

    def test_get_data(self):
        lb_id = Mock()
        lb_id.return_value = "foo"
        res = api.lb_get_data(self.conf, lb_id)
        self.assertTrue(self.api.lb_get_data.called, "method didn't call")
        self.asserEquals(res, "foo", "Something goes wrong")
#class WorkWithBalancer(TestCase):

#    def __init__(self):
#       self.conf = Mock()
#       self.lb = Balancer(self.conf)
#       self.lb_id = Mock()

#    def test_lb_show_details(self):
#        self.lb.loadFromDB(self.lb_id)
#        obj = {'loadbalancer':  self.lb.lb.convertToDict()}
#        lbobj = obj['loadbalancer']
#        lbobj['nodes'] = self.lb.rs
#        lbobj['virtualIps'] = self.lb.vips
#        lbobj['healthMonitor'] = self.lb.probes
#        self.assertEquals(self.lb.call_count, 5,\
#                        "lb calls incorrect number of times")
#
#    def test_create_lb(self):
        #params = Mock()
        #Test Step 1. Don't really know what to test.
#       bal_instance = Scheduller.Instance(self.conf)
#        device = bal_instance.getDeviceByID(Mock())
#        DeviceMap = Mock()
#        devmap = DeviceMap()
#        driver = devmap.getDriver(device)
#        context = driver.getContext(device)
#        load_b = self.lb.getLB()
#        load_b.device_id = device.id
#        self.assertEquals(device.call_count, 3,\
#                        "device calls incorrect number of times")
        #Test Step 2. Have no ideas already
#        self.lb.savetoDB()
        #Test Step 3
#        context.addParam('balancer', self.lb)
#        commands.create_loadbalancer(context, self.conf, driver, self.lb)
#        self.lb.update()
