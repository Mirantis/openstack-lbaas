CREATE TABLE loadbalancers(id INT, name TEXT, algorithm TEXT, status TEXT, created TEXT, updated TEXT);

CREATE TABLE serverfarms(id INT, lb_id INT,  name TEXT,
         type TEXT,  description TEXT, failAction TEXT, inbandHealthCheck TEXT, connFailureThreshCount TEXT,  resetTimeout TEXT,   resumeService TEXT,  transparent TEXT, 
         dynamicWorkloadScale TEXT,  vmProbeName TEXT, failOnAll TEXT,  partialThreshPercentage TEXT,   backInservice TEXT,   predictor_id INT,  retcodeMap TEXT,   status TEXT,    created TEXT,
         updated TEXT);

CREATE TABLE predictors( id INT, name TEXT, type TEXT);

CREATE TABLE rservers(id INT,   name TEXT,
         type TEXT, webHostRedir TEXT,   ipType TEXT,   IP TEXT,  port TEXT,  state TEXT,   opstate TEXT,    description TEXT,   failOnAll TEXT,   minCon INT,  maxCon INT, 
         weight INT,  rateBandwidth INT,   rateConn INT,    created TEXT,  updated TEXT, sf_id INT);


CREATE TABLE transactions (id INT, status TEXT, action TEXT, params TEXT);

CREATE TABLE devices (id INT,  name  TEXT, type TEXT, version TEXT, supports_IPv6 INT, require_VIP_IP INT, has_ACL INT, supports_VLAN INT);

#CREATE TABLE vips(id INT, ip_type TEXT, ip_addr TEXT, transport_proto TEXT, app_proto TEXT, port INT, vlan INT, sf_id INT, backup_sf_id INT);
CREATE TABLE vips(ICMPreply TEXT, KALAPprimaryOutOfServ TEXT, KALAPtagName TEXT, L7LoadBalancing TEXT, NAT TEXT, Port TEXT, SSLinitiation TEXT, 
        SSLproxyServName TEXT, VLAN TEXT, allVLANs TEXT, appAccelAndOpt TEXT, appProto TEXT, backupServerFarm TEXT, connParameterMap TEXT, created TEXT, defaultL7LBAction TEXT, 
        id INT, ip TEXT, ipType TEXT, name TEXT, proto TEXT, protocolInspect TEXT, serverFarm TEXT, status TEXT, sf_id INT, updated TEXT, virtIPmask TEXT);


CREATE TABLE vlans(ARPinspectType TEXT, IPaddr TEXT, MTU TEXT, RPF TEXT, UDPconfigCommands TEXT, actionForDBfit TEXT, actionForIPheaderOptions TEXT,
        adminStatus TEXT, aliasIPaddr TEXT, description TEXT, enableDHCPrelay TEXT, enableICMPguard TEXT, enableIPv6 TEXT, enableMACAddrAutogen TEXT,
        enableMACsticky TEXT, enableNormalization TEXT, enableSynCookieThreshValue TEXT, id INT, inputAccessGroup TEXT, inputPolicies TEXT, intType TEXT,
        ipv6GlobalIP TEXT, ipv6LinkLocalAddr TEXT, ipv6PeerLinkLocalAddr TEXT, ipv6UniqueLocalAddr TEXT, maxFragChainsAllowed TEXT, minFragMTUvalue TEXT, 
        minTTLipHeaderValue TEXT, netmask TEXT, outputAccessGroup TEXT, peerIPaddr TEXT, reassemblyTimeout TEXT, secondaryIPgroups TEXT);
