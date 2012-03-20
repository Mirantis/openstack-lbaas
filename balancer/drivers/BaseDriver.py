

class BaseDriver(object):
    def getContext(self):
        return BaseContext()

    def createRServer(self,  context,  rserver):
        pass
    
    def createServerFarm(self,  context,  serverfarm):
        pass
        
    def addRServerToSF(self,  context,  serverfarm,  rserver):
        pass
    
    def createProbe(self,  context,  probe):
        pass
    
    def attachProbeToSF(self,  context,  serverfarm,  probe):
        pass
    
    def createVIP(self,  context,  vip):
        pass
        
    def deleteRServerFromSF(self, context,  serverfarm,  rserver):
        pass
        
    def deleteRServer(self,  context,  rserver):
        pass
        
    def deleteServerFarm(self,  context,  serverfarm):
        pass
        
    def deleteVIP(self,  context,  vip):
        pass
        
    def deleteProbe(self,  context,  probe):
        pass
        
    def activateRServer(self,  context,  serverfarm,  rserver):
        pass
        
    def suspendRServer(self,  context,  serverfarm,  rserver):
        pass
        
    def createStickiness(self,  context,  vip,  sticky):
        pass
        
    def deleteStickiness(self,  context,  vip,  sticky):
        pass

class BaseContext(object):
    def __init__(self):
        self._params = {}
    
    def addParam(self,  name,  param):
        self._params[name] = param
    
    def getParam(self, name):
        return self._params.get(name,  None)


    

