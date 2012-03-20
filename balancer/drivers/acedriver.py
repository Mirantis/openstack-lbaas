import re

class acedriver():
    def __init__(self):
        pass
    
    def addVS(self, obj):
        pass
    
    def addRealServer(self, obj):
        TMP=""
        errorDescr = self.checkRealServerProperty(obj)
        if errorDescr != None:
            return errorDescr
        TMP=TMP+"<RS>\n"
        TMP=TMP+"<name>rsever "+obj.rs_type+" "+obj.rs_name+"<\\name>\n"
        TMP=TMP+"<ip>ip address "+obj.rs_ip+"<\\ip>\n"
        TMP=TMP+"<state>"+obj.rs_state+"<\\state>\n"
        TMP=TMP+"<\\RS>\n"
        return TMP
    
    def addSFarm(self, obj):
        TMP=""
        errorDescr = self.checkSFarmProperty(obj)
        if errorDescr != None:
            return errorDescr
        TMP=TMP+"<RS>\n"
        TMP=TMP+"<name>rsever "+obj.rs_type+" "+obj.rs_name+"<\\name>\n"
        TMP=TMP+"<ip>ip address "+obj.rs_ip+"<\\ip>\n"
        TMP=TMP+"<state>"+obj.rs_state+"<\\state>\n"
        TMP=TMP+"<\\RS>\n"
        return TMP 
 
    def checkRealServerProperty(self,  obj):
        errorDescr = ""
        if self.checkproperty_name(obj.rs_name) is False:
            errorDescr = errorDescr+"Wrong server name\n"
        if self.checkproperty_ip(obj.rs_ip) is False:
            errorDescr =  errorDescr+"Wrong ip address\n"
        if errorDescr != "":
            return errorDescr
        else:
           return None
    
    def checkproperty_name(self, name): #Not finished
        if re.match('^[\w\d]{0,32}$', name) == None:
            return False
        else:
            return True

    def checkproperty_ip(self,  ipaddr): #Not finished
        if re.match('^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$', ipaddr) == None:
            return False
        else:
            return True
        

class lb():
    def __init__(self):
        self.rs_type = "host"
        self.rs_name = "rs001"
        self.rs_ip = "250.1.1.1"
        self.rs_state = "inservice"
        self.rs_weight = "inservice"
        self.sfarm_name = "sfarm001"
        self.sfarm_probes = ["ICMP",  "HTTP"]

    def __getitem__(self, key):
        self.obj = key

rsObject = lb()
r = acedriver()
print r.addRealServer(rsObject)
