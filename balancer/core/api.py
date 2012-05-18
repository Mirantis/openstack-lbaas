# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools

import eventlet

def asynchronous(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        if kwargs.pop('async', True):
            eventlet.spawn(func, args, kwargs)
        else:
            return func(*args, **kwargs)

    return _inner

def lb_get_index(conf, tenant_id=''):
    store = Storage(conf)
    reader = store.getReader()
    return reader.getLoadBalancers(tenant_id)

def lb_find_for_vm(conf, vm_id, tenant_id=''):
    store = Storage(conf)
    reader = store.getReader()
    return reader.getLoadBalancersByVMid(vm_id,  tenant_id)

def lb_get_data(conf, lb_id):
    store = Storage(conf)
    reader = store.getReader()

    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    list = reader.getLoadBalancerById(lb_id)
    logger.debug("Got information: %s" % list)
    return list

def lb_show_details(conf, lb_id):
    store = Storage(conf)
    reader = store.getReader()

    lb = Balancer(conf)
    lb.loadFromDB(lb_id)
    obj = {'loadbalancer':  lb.lb.convertToDict()}
    lbobj = obj['loadbalancer']
    lbobj['nodes'] = lb.rs
    lbobj['virtualIps'] = lb.vips
    lbobj['healthMonitor'] = lb.probes
    logger.debug("Getting information about loadbalancer with id: %s" % lb_id)
    #list = reader.getLoadBalancerById(id)
    logger.debug("Got information: %s" % lbobj)
    return lbobj

@asynchronous
def create_lb(conf, **params):
    balancer_instance = Balancer(conf)
    #Step 1. Parse parameters came from request

    balancer_instance.parseParams(params)
    sched = Scheduller.Instance(conf)
    # device = sched.getDevice()
    device = sched.getDeviceByID(balancer_instance.lb.device_id)
    devmap = DeviceMap()
    driver = devmap.getDriver(device)
    context = driver.getContext(device)

    lb = balancer_instance.getLB()
    lb.device_id = device.id

    #Step 2. Save config in DB
    balancer_instance.savetoDB()

    #Step 3. Deploy config to device
    commands = makeCreateLBCommandChain(balancer_instance,  driver, \
    context, conf)
    context.addParam('balancer',  balancer_instance)
    deploy = Deployer(device,  context)
    deploy.commands = commands
    processing = Processing.Instance(conf)
    event = balancer.processing.event.Event( balancer.processing.event.EVENT_PROCESS, 
                                            deploy,  2)
    try:
        processing.put_event(event)
        
    except openstack.common.exception.Error:
        balancer_instance.lb.status = \
            balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
        balancer_instance.update()
        return
    except openstack.common.exception.Invalid:
        balancer_instance.lb.status = \
            balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
        balancer_instance.update()
        return

    #balancer_instance.lb.status = \
     #   balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
    #balancer_instance.update()
    #self._task.status = STATUS_DONE
    return lb.id
