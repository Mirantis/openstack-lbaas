import urllib2
import base64
import re 

url = "https://10.4.15.30:10443/bin/xml_agent"
username = "admin"
password = "cisco123"

r = urllib2.Request(url)

base64string = base64.encodestring(
                '%s:%s' % (username, password))[:-1]
authheader =  "Basic %s" % base64string
r.add_header("Authorization", authheader)

data = """xml_cmd=<request_xml>
%s
</request_xml>"""

handle = urllib2.urlopen(r, data)
print handle.geturl()
t = handle.read()
print t


class XmlSender:
    def __init__(self,  context):
        self.url = "https://%s:%s/bin/xml_agent" % (context.ip, context.port)

    def getParam(self, name):
        return self._params.get(name,  None)
    
    def deployConfig(self,  context,  command):
        request = urllib2.Request(self.url)
        
        base64str = base64.encodestring(
                                        '%s:%s' % (context.login, context.password))[:-1]
        
        authheader = "Basic %s" % base64str
        
        request.add_header("Authorization", authheader)
        
        data = """xml_cmd<request_xml>
        %s
        </request_xml>""" % command
        
        massage = urllib2.urlopen(request, data)
        return re.find(message.read(), 'XML_CMD_SUCCESS')
