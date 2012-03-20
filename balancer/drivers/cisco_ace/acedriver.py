class acedriver(BaseDriver):
    def init(self):
        pass
    
    def addRealServer(self, obj):
        TMP="<RealServer>\n"
        TMP=TMP+"rsever "+obj.type+" "+obj.name+"\n"
        if obj.type == "host":
            TMP=TMP+"ip address "+obj.IP+"\n"
            if obj.failOnAll != None: TMP=TMP+"fail-on-all\n"
        TMP=TMP+"conn-limit max "+str(obj.maxCon)+" min "+str(obj.minCon)+"\n"
        TMP=TMP+"weight "+str(obj.weight)+"\n"
        TMP=TMP+"description "+obj.description+"\n"
        if obj.type == "redirect" and obj.webHostRedir != "":
            TMP=TMP+"webhost-redirection "+obj.webHostRedir+"\n"
        if obj.rateBandwidth != "":
            TMP=TMP+"rate-limit bandwidth "+str(obj.rateBandwidth)+"\n"
        if obj.rateConn != "":
            TMP=TMP+"rate-limit connection "+str(obj.rateConn)+"\n"
        if obj.state != "":
            TMP=TMP+obj.state+"\n"
        for i in range(len(obj.probes)):
            TMP=TMP+"probe "+obj.probes[i]+"\n"
        TMP=TMP+"<\\RealServer>\n"
        return TMP

    def modReaslServer(self, obj):
        pass

    def delRealServer(self, obj):
        TMP="<RealServer>\n"
        TMP=TMP+"no rsever "+obj.name+"\n"
        TMP=TMP+"<\\RealServer>\n"
        return TMP

    def addSFarm(self, obj):
        TMP="<SFarm>\n"
        TMP=TMP+"rsever "+obj.type+" "+obj.name+"\n"
        for i in range(len(obj.probes)):
            TMP=TMP+"probe "+obj.probes[i]+"\n"
        if obj.failAction != None:
            TMP=TMP+"failaction "+obj.failAction+"\n"
        TMP=TMP+"description "+obj.description+"\n"
        if obj.type == "host":
            if obj.dynamicWorkloadScale != None: # Need to upgrade (may include VM's)
                TMP=TMP+"dws "+obj.failAction+"\n"
            if obj.failOnAll != None: 
                TMP=TMP+"fail-on-all\n"
            if obj.inbandHealthCheck == "remove":
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"remove"+obj.connFailureThreshCount
                if obj.resetTimeout != None:
                    TMP=TMP+" reset"+obj.resetTimeout
                if obj.resumeService != None:
                    TMP=TMP+" resume-service"+obj.resumeService
                TMP=TMP+"\n"
            elif obj.inbandHealthCheck == "log":
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"remove"+obj.connFailureThreshCount+"\n"
            else:
                TMP=TMP+"inband-health check"+obj.inbandHealthCheck+"\n"
            if obj.transparent != None:
                TMP=TMP+"transparent\n"
            if (obj.partialThreshPercentage != None) and (obj.backInservice != None):
                TMP=TMP+"partial-threshold "+obj.partialThreshPercentage+" back-inservice "+obj.backInservice+"\n"
        TMP=TMP+"predictor"+obj.predictor #Check it !!!
        TMP="<\\SFarm>\n"
        
    def SFarmaddRS(self, obj):
        TMP="<RealServer>\n"
        pass
    
    def SFarmdelRS(self, obj):
        pass
        
