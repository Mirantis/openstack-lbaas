from balancer.common.utils import Singleton
import balancer.processing.commandqueue
import balancer.processing.threadpool
import Queue
import balancer.processing.prioritized
import threading
import logging
logger = logging.getLogger(__name__)
@Singleton
class SharedObjects:
    def __init__(self):
        self._device_thread_pool = {}
        self._event_queue = Queue.PriorityQueue()
        self._default_priority = 10
        self._queue_lock = threading.Condition(threading.RLock())
        self._device_map_lock = threading.RLock()
        self._get_timeout = 100
        self._wait_timeout = 500
        
    def put_event(self,  event):
        self._queue_lock.acquire()
        try:
            if isinstance(event,  balancer.processing.prioritized.Prioritized):
                self._eventqueue.put(event,  event.priority)
            else:
                self._event_queue.put(event,  self._default_priority)
        finally:
            self._queue_lock.notify()
            self._queue_lock.release()
        
    def get_event(self):
        self._queue_lock.acquire()
        try:
            while True:
                    event = self._event_queue.get(True, timeout=self._get_timeout)
                    if event:
                        break
                    self._queue_lock.wait(self._wait_timeout)
            
            return event
        finally:
            self._queue_lock.release()
        
        
    def get_device_thread_pool(self,  device):
        self._device_map_lock.acquire()
        try:
            logger.debug("Getting device pool")
            if self._device_thread_pool.has_key(device.id):
                return self._device_thread_pool.get(device.id,  None)
            else:
                logger.debug("Creating new device pool")
                pool = balancer.processing.threadpool.ThreadPool(device.concurrent_deploys,
                                                                balancer.processing.threadpool.CommandExecutorThread()  )
                self._device_thread_pool[device.id] = pool
                return pool
        finally:
            self._device_map_lock.release()
    
    def getDevicePoolbyID(self,  device_id):
        self._device_map_lock.acquire()
        try:
            logger.debug("Getting device pool")
            if self._device_thread_pool.has_key(device_id):
                return self._device_thread_pool.get(device_id,  None)
            else:
                return None
        finally:
            self._device_map_lock.release()
    
    def joinAll(self):
        logger.info("Stopping all pools")
        for pool_id in self._device_thread_pool.keys():
            pool = self._device_thread_pool[pool_id]
            logger.debug("Waiting for pool #%s to complete and shutdown." % pool_id)
            pool.joinAll()
            
