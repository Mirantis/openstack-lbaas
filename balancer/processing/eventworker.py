import threading
from time import sleep
import balancer.processing.event
from balancer.processing.sharedobjects import SharedObjects
import balancer.loadbalancers.loadbalancer
from balancer.processing.threadpool import ThreadPool
import logging
logger = logging.getLogger(__name__)

class EventWorkerThread(threading.Thread):
    """ Pooled thread class. """
    
    threadSleepTime = 0.3

    def __init__(self, pool=None,  id=None):

        """ Initialize the thread and remember the pool. """
    
        threading.Thread.__init__(self)
        self.__pool = pool
        self.__isDying = False
        self.id = id
        if pool:
            self._shared = SharedObjects.Instance()
    
    def instance(self,  pool,  id):
        return EventWorkerThread(pool,  id)
        
    def run(self):

        """ Until told to quit, retrieve the next task and execute
        it, calling the callback if any.  """
        
        while self.__isDying == False:
            
            event = self.__pool.getNextTask()
            # If there's nothing to do, just sleep a bit
            if event is None:
                sleep(EventWorkerThread.threadSleepTime)
            else:
                self.__pool.set_status(self.id,  ThreadPool.STATE_WORKING )
                self.dispatch(event)
                self.__pool.set_status(self.id,  ThreadPool.STATE_WAITING)
        logger.debug("[%s]Finishing thread work." % threading.currentThread())
    
    def goAway(self):

        """ Exit the run loop next time through."""
        
        self.__isDying = True

    def dispatch(self,  event):
        logger.debug('Got event. Processing.')
        if event.gettype() == balancer.processing.event.EVENT_PROCESS:
            logger.debug('Got event with type Processing.')
            data = event.getdata()
            device = data.device
            logger.debug('Put item to device pool')
            pool = self._shared.get_device_thread_pool(device)
            
            pool.queueTask(data)
            return
        if event.gettype() == balancer.processing.event.EVENT_DONE:
            logger.debug('Got event of Done type')
            data = event.getdata()
            balancer_instance = data.context.getParam('balancer')
            status = data.context.getParam('status')
            if status == 'done':
                balancer_instance.lb.status = \
                balancer.loadbalancers.loadbalancer.LB_ACTIVE_STATUS
            if status == 'error':
                balancer_instance.lb.status = \
                balancer.loadbalancers.loadbalancer.LB_ERROR_STATUS
            balancer_instance.update()
            return
                
        
    
