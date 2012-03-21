CREATE TABLE loadbalancers(id INT, name TEXT, algorithm TEXT, status TEXT, created TEXT, updated TEXT);

CREATE TABLE serverfarms(id INT, lb_id INT,  name TEXT,
         type TEXT,  description TEXT, failAction TEXT, inbandHealthCheck TEXT, connFailureThreshCount TEXT,  resetTimeout TEXT,   resumeService TEXT,  transparent TEXT, 
         dynamicWorkloadScale TEXT,  vmProbeName TEXT, failOnAll TEXT,  partialThreshPercentage TEXT,   backInservice TEXT, probes TEXT , rservers TEXT, predictor_id INT,  
         retcodeMap TEXT,   status TEXT,    created TEXT,  updated TEXT);

CREATE TABLE predictors( id INT, name TEXT, type TEXT);

CREATE TABLE rservers(id INT, sf_id INT, name TEXT,
         type TEXT, webHostRedir TEXT,   ipType TEXT,   IP TEXT,  port TEXT,  state TEXT,   opstate TEXT,    description TEXT,   failOnAll TEXT,   minCon INT,  maxCon INT, 
         weight INT,  probes TEXT, rateBandwidth INT,   rateConn INT,    created TEXT,  updated TEXT);


CREATE TABLE transactions (id INT, status TEXT, action TEXT, params TEXT);

CREATE TABLE devices (id INT,  name  TEXT, type TEXT, version TEXT, supports_IPv6 INT, require_VIP_IP INT, has_ACL INT, supports_VLAN INT);

#CREATE TABLE vips(id INT, ip_type TEXT, ip_addr TEXT, transport_proto TEXT, app_proto TEXT, port INT, vlan INT, sf_id INT, backup_sf_id INT);
CREATE TABLE vips(id INT, sf_id INT, name TEXT, ipType TEXT, ip TEXT, virtIPmask TEXT, proto TEXT, appProto TEXT, Port TEXT, allVLANs TEXT, VLAN TEXT,
        connParameterMap  TEXT,  KALAPtagName TEXT,  KALAPprimaryOutOfServ TEXT,  ICMPreply TEXT,  status TEXT,  protocolInspect TEXT,  appAccelAndOpt TEXT,
        L7LoadBalancing TEXT,  serverFarm TEXT,  backupServerFarm TEXT,  SSLproxyServName TEXT,  defaultL7LBAction TEXT,  SSLinitiation TEXT,  NAT TEXT,
        created TEXT,  updated TEXT);


CREATE TABLE vlans(id   INT, description   TEXT, intType   TEXT, IPaddr   TEXT, aliasIPaddr   TEXT, peerIPaddr   TEXT, netmask   TEXT, adminStatus   TEXT, 
        enableMACsticky   TEXT, enableNormalization   TEXT, enableIPv6   TEXT, ipv6GlobalIP   TEXT, ipv6UniqueLocalAddr   TEXT, ipv6LinkLocalAddr   TEXT, 
        ipv6PeerLinkLocalAddr   TEXT, enableICMPguard   TEXT, enableDHCPrelay   TEXT, RPF   TEXT, reassemblyTimeout   TEXT, maxFragChainsAllowed   TEXT, minFragMTUvalue   TEXT, 
        MTU   TEXT, actionForIPheaderOptions   TEXT, enableMACAddrAutogen   TEXT, minTTLipHeaderValue   TEXT, enableSynCookieThreshValue   TEXT, actionForDBfit   TEXT, 
        ARPinspectType   TEXT, UDPconfigCommands   TEXT, secondaryIPgroups   TEXT, inputPolicies   TEXT, inputAccessGroup   TEXT, outputAccessGroup   TEXT);
