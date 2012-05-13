import threading
import balancer.processing.prioritized

EVENT_PROCESS = 1
EVENT_DONE = 2

class Event(balancer.processing.prioritized.Prioritized):

    def __init__(self, type,  data,  priority = 10):
        balancer.processing.prioritized.Prioritized.__init__(self, priority)
        self._type = type
        self._data = data
        self.lock = threading.Lock()
    
    def gettype(self):
        self.lock.acquire()
        type= self._type
        self.lock.release()
        return type
    
    def settype(self,  type):
        self.lock.acquire()
        self._type = type
        self.lock.release()
        
    def getdata(self):
        return self._data
