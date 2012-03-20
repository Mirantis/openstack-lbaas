class acedriver():
    def __init__(self):
        pass
    
    def addSFarm(self, obj):
        TMP="<SFarm>\n"
        TMP=TMP+"rsever "+obj._type+" "+obj._name+"\n"
        for i in range(len(obj._probes)):
            TMP=TMP+"probe "+obj._probes[i]+"\n"
        if obj._failAction != None:
            TMP=TMP+"failaction "+obj._failAction+"\n"
        TMP=TMP+"description "+obj._description+"\n"
        if obj._type == "host":
            if obj._dynamicWorkloadScale != None: # Need to upgrade (may include VM's)
                TMP=TMP+"dws "+obj._failAction+"\n"
            if obj._failOnAll != None: 
                TMP=TMP+"fail-on-all\n"
            if obj._inbandHealthCheck == "remove":
                TMP=TMP+"inband-health check"+obj._inbandHealthCheck+"remove"+obj._connFailureThreshCount
                if obj._resetTimeout != None:
                    TMP=TMP+" reset"+obj._resetTimeout
                if obj._resumeService != None:
                    TMP=TMP+" resume-service"+obj._resumeService
                TMP=TMP+"\n"
            elif obj._inbandHealthCheck == "log":
                TMP=TMP+"inband-health check"+obj._inbandHealthCheck+"remove"+obj._connFailureThreshCount+"\n"
            else:
                TMP=TMP+"inband-health check"+obj._inbandHealthCheck+"\n"
            if obj._transparent != None:
                TMP=TMP+"transparent\n"
            if (obj._partialThreshPercentage != None) and (obj._backInservice != None):
                TMP=TMP+"partial-threshold "+obj._partialThreshPercentage+" back-inservice "+obj._backInservice+"\n"
        TMP=TMP+"predictor"+obj._predictor #Check it !!!
    
    def addRealServer(self, obj):
        TMP="<RealServer>\n"
        TMP=TMP+"rsever "+obj._type+" "+obj._name+"\n"
        if obj._type == "host":
            TMP=TMP+"ip address "+obj._IP+"\n"
            if obj._failOnAll != None: TMP=TMP+"fail-on-all\n"
        TMP=TMP+"conn-limit max "+str(obj._maxCon)+" min "+str(obj._minCon)+"\n"
        TMP=TMP+"weight "+str(obj._weight)+"\n"
        TMP=TMP+"description "+obj._description+"\n"
        if obj._type == "redirect" and obj._webHostRedir != "":
            TMP=TMP+"webhost-redirection "+obj._webHostRedir+"\n"
        if obj._rateBandwidth != "":
            TMP=TMP+"rate-limit bandwidth "+str(obj._rateBandwidth)+"\n"
        if obj._rateConn != "":
            TMP=TMP+"rate-limit connection "+str(obj._rateConn)+"\n"
        if obj._state != "":
            TMP=TMP+obj._state+"\n"
        for i in range(len(obj._probes)):
            TMP=TMP+"probe "+obj._probes[i]+"\n"
        TMP=TMP+"<\\RealServer>\n"
        return TMP

    def delRealServer(self, obj):
        TMP="<RealServer>\n"
        TMP=TMP+"no rsever "+obj._name+"\n"
        TMP=TMP+"<\\RealServer>\n"
        return TMP

    def updateReaslServer(self, obj):
        pass
    
    

y = ServerFarm()
x = acedriver()
print x.addRealServer(y)
