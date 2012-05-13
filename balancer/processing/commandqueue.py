import Queue
from balancer.processing.prioritized import Prioritized

class DeviceCommandQueue:
    def __init__(self,):
        self.queue = Queue.PriorityQueue()
        
        self.default = 10
    
    def put(self,  item):
        if isinstance(item,  Prioritized):
            self.queue.put(item,  item.priority)
        else:
            self.queue.put(item,  self.default)
    
    def get(self):
        return self.queue.get()
        
    def empty(self):
        return self.queue.empty()
    
    def size(self):
        return self.queue.qsize()
