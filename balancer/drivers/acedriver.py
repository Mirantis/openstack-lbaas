import re

class acedriver():
    def __init__(self):
        self.healthprobe = "ICMP"
    
    def __str__(self):
        return "oops"

    def AddLB(self, dict): #.rs_name, .rs_ip, ._sfarm
        return self.checkproperty_ip(dict.rs_ip)
        
    def checkproperty_name(self, name):
		if re.match (name, "[a-z]"):
			return 1
		else:
			return "Wrong name"

    def checkproperty_ip(self,  ipaddr):
        if re.match(ipaddr, '^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$'):
			return "match !"
        else:
			return "Wrong"


class lb():
    def __init__(self):
        self.rs_name = "rs001"
        self.rs_ip = "10.1.1.1"
        self.sfarm_name = "sfarm001"


rsObject = lb()
#print rsObject
r = acedriver()
print r.AddLB(rsObject)
