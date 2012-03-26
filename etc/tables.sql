CREATE TABLE loadbalancers(id TEXT, name TEXT, algorithm TEXT, status TEXT, created TEXT, updated TEXT);

CREATE TABLE serverfarms(id TEXT, lb_id TEXT,  name TEXT,
         type TEXT,  description TEXT, failAction TEXT, inbandHealthCheck TEXT, connFailureThreshCount TEXT,  resetTimeout TEXT,   resumeService TEXT,  transparent TEXT, 
         dynamicWorkloadScale TEXT,  vmProbeName TEXT, failOnAll TEXT,  partialThreshPercentage TEXT,   backInservice TEXT,   
         retcodeMap TEXT,   status TEXT,    created TEXT,  updated TEXT);

CREATE TABLE predictors( type TEXT, id TEXT, name TEXT, maskType TEXT, ipNetmask TEXT, ipv6Prefix TEXT, beginPattern TEXT, endPattern TEXT, length TEXT, offsetBytes TEXT,
        cookieName TEXT, customHeader TEXT, definedHeader TEXT, accessTime TEXT, samples TEXT, slowStartDur TEXT, snmpProbe TEXT, autoAdjust TEXT, weightConn TEXT,
        responseType TEXT, sf_id TEXT);

CREATE TABLE rservers(id TEXT, sf_id TEXT, name TEXT,
         type TEXT, webHostRedir TEXT,   ipType TEXT,   address TEXT,  port TEXT,  state TEXT,   opstate TEXT,    description TEXT,   failOnAll TEXT,   minCon INT,  maxCon INT, 
         weight INT,  probes TEXT, rateBandwidth INT,   rateConnection INT,    backupRS TEXT,  backupRSport TEXT,  created TEXT,  updated TEXT, cookieStr TEXT);


CREATE TABLE transactions (id TEXT, status TEXT, action TEXT, params TEXT);

CREATE TABLE devices (id TEXT,  name  TEXT, type TEXT, version TEXT, supports_ipv6 INT, requires_vip_ip INT, has_acl INT, supports_vlan INT, ip TEXT, port TEXT, user TEXT, password TEXT, vip_vlan TEXT);

CREATE TABLE vips(id TEXT, sf_id TEXT, name TEXT, ipVersion TEXT, address TEXT, mask TEXT, proto TEXT, appProto TEXT, port TEXT, allVLANs TEXT, VLAN TEXT,
        connParameterMap  TEXT,  KALAPtagName TEXT,  KALAPprimaryOutOfServ TEXT,  ICMPreply TEXT,  status TEXT,  protocolInspect TEXT,  appAccelAndOpt TEXT,
        L7LoadBalancing TEXT,  lb_id TEXT,  backupServerFarm TEXT,  SSLproxyServName TEXT,  defaultL7LBAction TEXT,  SSLinitiation TEXT,  NAT TEXT,
        created TEXT,  updated TEXT);


CREATE TABLE vlans(id   TEXT, description   TEXT, intType   TEXT, IPaddr   TEXT, aliasIPaddr   TEXT, peerIPaddr   TEXT, netmask   TEXT, adminStatus   TEXT, 
        enableMACsticky   TEXT, enableNormalization   TEXT, enableIPv6   TEXT, ipv6GlobalIP   TEXT, ipv6UniqueLocalAddr   TEXT, ipv6LinkLocalAddr   TEXT, 
        ipv6PeerLinkLocalAddr   TEXT, enableICMPguard   TEXT, enableDHCPrelay   TEXT, RPF   TEXT, reassemblyTimeout   TEXT, maxFragChainsAllowed   TEXT, minFragMTUvalue   TEXT, 
        MTU   TEXT, actionForIPheaderOptions   TEXT, enableMACAddrAutogen   TEXT, minTTLipHeaderValue   TEXT, enableSynCookieThreshValue   TEXT, actionForDBfit   TEXT, 
        ARPinspectType   TEXT, UDPconfigCommands   TEXT, secondaryIPgroups   TEXT, inputPolicies   TEXT, inputAccessGroup   TEXT, outputAccessGroup   TEXT);

CREATE TABLE probes(sf_id TEXT,delay TEXT,attemptsBeforeDeactivation TEXT,timeout TEXT, type  TEXT, id  TEXT, name  TEXT, description  TEXT, probeInterval  TEXT, passDetectInterval  TEXT, failDetect  TEXT, passDetectCount  TEXT,
        receiveTimeout  TEXT, isRouted  TEXT, port  TEXT, 
        domainName TEXT, sendData TEXT, destIP TEXT, tcpConnTerm TEXT, openTimeout TEXT, requestMethodType TEXT, requestHTTPurl TEXT, appendPortHostTag TEXT,
        userName TEXT, password TEXT, expectRegExp TEXT, expectRegExpOffset TEXT, hash TEXT, hashString TEXT, headerName TEXT, headerValue TEXT,minExpectStatus TEXT, 
        maxExpectStatus TEXT, cipher TEXT, SSLversion TEXT,
        maibox TEXT, requestCommand TEXT,  userSecret TEXT, NASIPaddr TEXT, requareHeaderValue TEXT, proxyRequareHeaderValue TEXT, requestURL TEXT, 
        scriptName TEXT, scriptArgv TEXT,  copied TEXT,  proto TEXT,  sourceFileName TEXT,  SNMPComm TEXT,  SNMPver TEXT,  maxCPUburstThresh TEXT, minCPUburstThresh TEXT,
        maxMemBurstThresh TEXT, minMemBurstThresh TEXT, VMControllerName TEXT);
