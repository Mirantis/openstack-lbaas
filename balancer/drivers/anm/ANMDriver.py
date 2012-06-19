import logging

from balancer.drivers.cisco_ace.Context import Context
from balancer.drivers.base_driver import is_sequence
from balancer.drivers.cisco_ace.ace_5x_driver import AceDriver

from suds.client import Client

logger = logging.getLogger(__name__)


class ANMSpecificContext(Context):
    def __init__(self, ip, port, login, password, contextName):
        super(ANMSpecificContext, self).__init__(ip, port, login, password)
        self.contextName = contextName
        self.templateInstances = {}


class ANMDriver(AceDriver):
    def __init__(self, anmIp, anmLogin, anmPassword):
        super(ANMDriver, self).__init__()
        self.anmIp = anmIp
        self.anmLogin = anmLogin
        self.anmPassword = anmPassword
        self.operationClient = Client(
            "http://%s:8080/anm/OperationManager?wsdl" % self.anmIp)
        self.templateClient = Client(
            "http://%s:8080/anm/ApplicationTemplateManager?wsdl" % self.anmIp)

    def getContext(self,  dev):
        logger.debug("Creating context with params: IP %s, Port: %s",
                dev.ip, dev.port)
        return ANMSpecificContext(dev.ip, dev.port, dev.user, dev.password,
                    "dmitryme")

######## Work Methods
######## Commented out methods are inherited

#   def createRServer(self,  context,  rserver):

#   def deleteRServer(self,  context,  rserver):

#    def activateRServer(self,  context,  serverfarm,  rserver):
#        sid = self.login()
#        try:
#            deviceId = self.createSudsDeviceID(context)
#            sfRServer = self.createSudsServerFarmRServer(serverfarm, rserver)
#            self.operationClient.service.activateServerfarmRserver(sid,
#                deviceId, sfRServer, "OpenstackLB wants this rserver up!")
#        finally:
#            self.logout(sid)

#    def suspendRServer(self,  context,  serverfarm,  rserver):
#        sid = self.login()
#        try:
#            deviceId = self.createSudsDeviceID(context)
#            sfRServer = self.createSudsServerFarmRServer(serverfarm, rserver)
#            self.operationClient.service.suspendServerfarmRserver(sid,
#                deviceId, sfRServer, "Suspend",
#                "OpenstackLB wants this rserver down!")
#        finally:
#            self.logout(sid)

#    def createProbe(self,  context,  probe):
#        raise NotImplementedError("ANM Driver can not create probes")

#    def deleteProbe(self,  context,  probe):
#        raise NotImplementedError("ANM Driver can not delete probes")

#   def createServerFarm(self,  context,  serverfarm):

#   def deleteServerFarm(self,  context,  serverfarm):

    # backup-rserver is not supported
#    def addRServerToSF(self,  context,  serverfarm,  rserver):
#        sid = self.login()
#        try:
#            deviceId = self.createSudsDeviceID(context)
#            rServer = self.createSudsRServer(rserver)
#            port = 0
#            if hasattr(rserver, 'port'):
#                port = rserver.port
#            self.operationClient.service.addRserverToServerfarm(sid, deviceId,
#                serverfarm.name, rServer, port)
#        finally:
#            self.logout(sid)

#    def deleteRServerFromSF(self, context,  serverfarm,  rserver):
#        sid = self.login()
#        try:
#            deviceId = self.createSudsDeviceID(context)
#            sfRServer = self.createSudsServerFarmRServer(serverfarm, rserver)
#            self.operationClient.service.removeRserverFromServerfarm(sid,
#                deviceId, sfRServer)
#        finally:
#            self.logout(sid)

#    def addProbeToSF(self,  context,  serverfarm,  probe):
#        raise NotImplementedError(
#            "ANM Driver can not add probes to server farm")

 #   def deleteProbeFromSF(self,  context,  serverfarm,  probe):
 #       raise NotImplementedError(
#            "ANM Driver can not delete probes from server farm")

    def create_stickiness(self, sticky):
        raise NotImplementedError("ANM Driver can not enable stickness")

    def delete_stickiness(self, sticky):
        raise NotImplementedError("ANM Driver can not disable stickness")

    def createVIP(self,  context,  vip,  sfarm):
        values = {}
        values["service"] = {}
        values["network"] = {}
        values["service"]["name"] = vip.name
        values["service"]["vip"] = vip.address
        values["service"]["port"] = vip.port
        values["service"]["sfarm_name"] = sfarm.name
        if hasattr(vip, 'backupServerFarm') and vip.backupServerFarm != "":
            values["service"]["use_backup_sfarm"] = "true"
            values["service"]["backup_sfarm_name"] = vip.backupServerFarm
        else:
            values["service"]["use_backup_sfarm"] = "false"
            values["service"]["backup_sfarm_name"] = ""

        values["service"]["sticky"] = "false"

        values["network"]["device"] = ""
        if self.checkNone(vip.allVLANs):
            values["network"]["vlans"] = "ALL_VLAN"
        elif is_sequence(vip.VLAN):
            values["network"]["vlans"] = ",".join(vip.VLAN)
        else:
            values["network"]["vlans"] = vip.VLAN
        values["network"]["autoNat"] = "true"

        sid = self.login()
        try:
            definition = self.fetchTemplateDefinition(sid,
                    "OpenstackLB-Basic-HTTP-adv")
            inputs = self.fetchTemplateImputs(sid, definition)
            self.fillTemplateInputs(inputs, values)
            deviceId = self.createSudsDeviceID(context)
            instance = self.templateClient.service.createTemplateInstance(sid,
                    deviceId, definition, inputs)
            context.templateInstances[vip.name] = instance
        finally:
            self.logout(sid)

    def deleteVIP(self,  context,  vip):
        sid = self.login()
        try:
            instance = context.templateInstances[vip.name]
            deviceId = self.createSudsDeviceID(context)
            self.templateClient.service.deleteTemplateInstance(sid, deviceId,
                    instance)
        finally:
            self.logout(sid)

######## Utilities
    def login(self):
        return self.operationClient.service.login(self.anmLogin,
                self.anmPassword)

    def logout(self, sid):
        self.operationClient.service.logout(sid)

    def createSudsDeviceID(self, context):
        deviceId = self.operationClient.factory.create('DeviceID')
        deviceId.name = context.contextName
        deviceId.ipAddr = context.ip
        deviceId.deviceType.value = "VIRTUAL_CONTEXT"
        return deviceId

    def createSudsServerFarmRServer(self, serverfarm, rserver):
        sfRServer = self.operationClient.factory.create('SfRserver')
        sfRServer.serverfarmName = serverfarm.name
        sfRServer.realserverName = rserver.name
        sfRServer.adminState.value = "IS"
        if hasattr(rserver, "port"):
            sfRServer.port = rserver.port
        else:
            sfRServer.port = 0

        if hasattr(rserver, "weight"):
            sfRServer.weight = rserver.weight
        else:
            sfRServer.weight = 8

        return sfRServer

    def createSudsRServer(self, rserver):
        rServer = self.operationClient.factory.create('Rserver')
        rServer.name = rserver.name
        if hasattr(rserver, 'state'):
            if rserver.state.lower() == "inservice":
                rServer.state = "IS"
            elif rserver.state.lower() == "standby":
                rServer.state = "ISS"
            else:
                rServer.state = "OOS"
        else:
            rServer.state = "IS"

        if hasattr(rserver, "weight"):
            rServer.weight = rserver.weight
        else:
            rServer.weight = 8

        return rServer

    def fetchTemplateDefinition(self, sid, templateName):
        listOfDefs = self.templateClient.service.listTemplateDefinitions(sid)
        for definition in listOfDefs['item']:
            if definition.name == templateName:
                return definition
        raise RuntimeError("No such template found: %s" % templateName)

    def fetchTemplateImputs(self, sid, templateDefinition):
        return self.templateClient.service.getTemplateDefinitionMetadata(sid,
                templateDefinition)

    def fillTemplateInputs(self, templateInputs, values):
        for inputGroup in templateInputs['item']:
            if inputGroup.name in values:
                self.fillTemplateGroupInputs(inputGroup, inputGroup.name,
                        values[inputGroup.name])
            else:
                print "Ops, don't have group %s in values" % inputGroup.name

    def fillTemplateGroupInputs(self, element, groupName, mapping):
        if not hasattr(element, 'childElements'):
            return
        for inp in element.childElements:
            if hasattr(inp, 'name'):
                if inp.name in mapping:
                    inp.userData = mapping[inp.name]
                else:
                    print "Ops, don't have value for group %s, input %s" % (
                                                        groupName, inp.name)
            self.fillTemplateGroupInputs(inp, groupName, mapping)



#values = {}
#values["service"] = {}
#values["network"] = {}
#values["service"]["name"] = "OpenstackLB-app"
#values["service"]["vip"] = "10.4.15.33"
#values["service"]["port"] = "110"
#values["service"]["sfarm_name"] = "sftest"
#values["service"]["use_backup_sfarm"] = "true"
#values["service"]["backup_sfarm_name"] = "sftest-backup"
#values["service"]["sticky"] = "false"

#values["network"]["device"] = "ace30:dmitryme"
#values["network"]["vlans"] = "2"
#values["network"]["autoNat"] = "true"
