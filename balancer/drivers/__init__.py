import logging

from balancer.common import cfg
from balancer.common import utils
from balancer.db import api as db_api


LOG = logging.getLogger(__name__)

drivers_opt = cfg.ListOpt('device_drivers',
        default=[
            'ace=balancer.drivers.cisco_ace.ace_driver.AceDriver',
            'haproxy=balancer.drivers.haproxy.haproxy_driver.HaproxyDriver',
        ],
        help="Balancer devices' drivers.")

DEVICE_DRIVERS = {}


def get_device_driver(conf, device_id):
    try:
        return DEVICE_DRIVERS[device_id]
    except KeyError:
        conf.register_opt(drivers_opt)
        drivers = {}
        for driver_str in conf.device_drivers:
            driver_type, _sep, driver = driver_str.partition('=')
            drivers[driver_type.lower()] = utils.import_class(driver)

        device_ref = db_api.device_get(conf, device_id)
        try:
            cls = drivers[device_ref['type'].lower()]
        except KeyError:
            raise NotImplementedError("Driver not found for type %s" % \
                                        (device_ref['type'],))
        DEVICE_DRIVERS[device_id] = cls(conf, device_ref)
        return DEVICE_DRIVERS[device_id]


def delete_device_driver(conf, device_id):
    try:
        del DEVICE_DRIVERS[device_id]
    except KeyError:
        LOG.debug("Driver for device %r not initialized", device_id)
