import threading
from time import sleep
import balancer.processing.commandqueue
import balancer.processing.processing
import balancer.processing.event
from balancer.processing.prioritized import Prioritized
import logging


logger = logging.getLogger(__name__)

class ThreadPool:

    """Flexible thread pool class.  Creates a pool of threads, then
    accepts tasks that will be dispatched to the next available
    thread."""
    STATE_WORKING = 'working'
    STATE_WAITING = 'waiting'
    
    def __init__(self, numThreads,  thread_type):

        """Initialize the thread pool with numThreads workers."""
        
        self.__threads = []
        self.__thread_count = 0
        self.__resizeLock = threading.Condition(threading.Lock())
        self.__taskLock = threading.Condition(threading.Lock())
        self.__status_lock = threading.Lock()
        self.__tasks = balancer.processing.commandqueue.DeviceCommandQueue()
        self.__isJoining = False
        self.__thread_type = thread_type
        self.__thread_status={}
        self.setThreadCount(numThreads)

    def set_status(self,  id,  status):
        self.__status_lock.acquire()
        try:
            self.__thread_status[id] = status
        finally:
            self.__status_lock.release()
    
    def get_status(self,  id):
        self.__status_lock.acquire()
        try:
            status = self.__thread_status[id]
            return status
        finally:
            self.__status_lock.release()
    
    def getQueueSize(self):
        return self.__tasks.size()
            
    def setThreadCount(self, newNumThreads):

        """ External method to set the current pool size.  Acquires
        the resizing lock, then calls the internal version to do real
        work."""
        
        # Can't change the thread count if we're shutting down the pool!
        if self.__isJoining:
            return False
        
        self.__resizeLock.acquire()
        try:
            self.__setThreadCountNolock(newNumThreads)
        finally:
            self.__resizeLock.release()
        return True

    def __setThreadCountNolock(self, newNumThreads):
        
        """Set the current pool size, spawning or terminating threads
        if necessary.  Internal use only; assumes the resizing lock is
        held."""
        logger.debug("Creating new thread pool with thread num #: %s" % newNumThreads)
        # If we need to grow the pool, do so
        count = len(self.__threads)
        local_new = int(newNumThreads)
        while local_new > count:
            newThread = self.__thread_type.instance(self, count)
            self.__threads.append(newThread)
            logger.debug("Starting new thread...%s %s by thread: %s"% (local_new,  count,  threading.currentThread()))
            newThread.start()
            self.__thread_status[count] = ThreadPool.STATE_WAITING
            count += 1


            

    def getThreadCount(self):

        """Return the number of threads in the pool."""
        
        self.__resizeLock.acquire()
        try:
            return len(self.__threads)
        finally:
            self.__resizeLock.release()

    def queueTask(self, task):

        """Insert a task into the queue.  task must be callable;
        args and taskCallback can be None."""
        """
        If got signal to shutdown do not accept new processing requests. We need to process only DONE events from working threads.
        """
        if isinstance(task,   balancer.processing.event.Event):
            if (self.__isJoining == True) and (task.gettype() ==  balancer.processing.event.EVENT_PROCESS):
                return False
        
        
        self.__taskLock.acquire()
        try:
            logger.debug("threadPool adding new task")
            self.__tasks.put(task)
            return True
        finally:
            self.__taskLock.release()
    
    def donotAcceptProcessing(self):
        self.__isJoining = True

    def waitForEmptyQueue(self):
        while not self.__tasks.empty():
            sleep(0.3)
            
    def getNextTask(self):

        """ Retrieve the next task from the task queue.  For use
        only by ThreadPoolThread objects contained in the pool."""
        
        self.__taskLock.acquire()
  
        try:
            if self.__tasks.empty():
                return None
            else:
                logger.debug("threadPool: return new task to worked")
                return self.__tasks.get()
        finally:
            self.__taskLock.release()
    
    def joinAll(self, waitForTasks = True, waitForThreads = True):

        """ Clear the task queue and terminate all pooled threads,
        optionally allowing the tasks and threads to finish."""
        
        # Mark the pool as joining to prevent any more task queueing
        self.__isJoining = True

        # Wait for tasks to finish
        logger.debug("Threadpool: waiting for all tasks to be finished.")
        if waitForTasks:
            while not self.__tasks.empty():
                logger.debug("Threadpool: Task queue is not empty. %s" % self.__tasks.size())
                sleep(.3)

        # Tell all the threads to quit
        logger.debug("Threadpool: shutdown threads...")
        self.__resizeLock.acquire()
        try:
            for t in self.__threads:
                t.goAway()
            self.__isJoining = True

            # Wait until all threads have exited
            if waitForThreads:
                for t in self.__threads:
                    while t.isAlive():
                        t.join(0.5)
                        logger.debug("Waiting for thread %s" % t.id)
                    del t

            # Reset the pool for potential reuse
            self.__isJoining = False
        finally:
            self.__resizeLock.release()


        
class CommandExecutorThread(threading.Thread):

    """ Pooled thread class. """
    
    threadSleepTime = 1

    def __init__(self, pool=None,  id=None):

        """ Initialize the thread and remember the pool. """
        
        threading.Thread.__init__(self)
        self.__pool = pool
        self.__isDying = False
        self.id = id
    
    def instance(self,  pool,  id):
        return CommandExecutorThread(pool,  id)
        
    def run(self):

        """ Until told to quit, retrieve the next task and execute
        it, calling the callback if any.  """
        
        while self.__isDying == False:
            commands = self.__pool.getNextTask()
            # If there's nothing to do, just sleep a bit
            if commands is None:
                sleep(CommandExecutorThread.threadSleepTime)
            else:
                try:
                    self.__pool.set_status(self.id,  ThreadPool.STATE_WORKING)
                    logger.debug("Worker: Got new task. Executing.")
                    commands.execute()
                    commands.context.addParam('status',  'done')
                except:
                    commands.context.addParam('status',  'error')
                logger.debug("Worker: Executing is done.")
                event = balancer.processing.event.Event(balancer.processing.event.EVENT_DONE, commands, 2)
                processing =  balancer.processing.processing.Processing.Instance()
                processing.put_event(event)
                self.__pool.set_status(self.id,  ThreadPool.STATE_WAITING)
        logger.debug("[%s]Finishing thread work." % threading.currentThread())
                
    
    def goAway(self):

        """ Exit the run loop next time through."""
        
        self.__isDying = True
