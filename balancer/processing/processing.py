import  balancer.processing.threadpool

from balancer.processing.eventworker import EventWorkerThread
from balancer.common.utils import  Singleton
import logging
logger = logging.getLogger(__name__)

@Singleton
class Processing:
    def __init__(self, conf):
        
        self._workers = 4
        self._processing_pool = balancer.processing.threadpool.ThreadPool( self._workers,  EventWorkerThread())
        self._conf = conf
        
    def put_event(self,  event):
        logger.debug("Putting event into queue")
        self._processing_pool.queueTask(event)
    
    def joinAll(self):
        self._processing_pool.joinAll()
        
    def donotAcceptProcessing(self):
        self._processing_pool.donotAcceptProcessing()
    
    def waitForEmptyQueue(self):
        self._processing_pool.waitForEmptyQueue()
    
    def getThreadCount(self):
        return self._processing_pool.getThreadCount()
        
    def getThreadStatus(self,  id):
        return self._processing_pool.get_status(id)
    
    def getQueueSize(self):
        return self._processing_pool.getQueueSize()
        
if __name__ == '__main__':
    proc = Processing.Instance(None)
    quit()
