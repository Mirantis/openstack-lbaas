CREATE DATABASE balancer ;
use balancer;
CREATE TABLE tenants(id VARCHAR(60), name VARCHAR(60));

CREATE TABLE tenantdevices(tenant_id VARCHAR(60), device_id VARCHAR(60));

CREATE TABLE loadbalancers(id VARCHAR(60), name VARCHAR(60), protocol VARCHAR(60), transport VARCHAR(60), algorithm VARCHAR(60), status VARCHAR(60), created VARCHAR(60), updated VARCHAR(60), device_id VARCHAR(60), tenant VARCHAR(60), deployed VARCHAR(60), tenant_id VARCHAR(60), tenant_name VARCHAR(60));
CREATE INDEX loadbalancers_id_idx ON loadbalancers (id);

CREATE TABLE serverfarms(id VARCHAR(60), lb_id VARCHAR(60),  name VARCHAR(60),
         type VARCHAR(60),  description VARCHAR(60), failAction VARCHAR(60), inbandHealthCheck VARCHAR(60), connFailureThreshCount VARCHAR(60),  resetTimeout VARCHAR(60),   resumeService VARCHAR(60),  transparent VARCHAR(60), 
         dynamicWorkloadScale VARCHAR(60),  vmProbeName VARCHAR(60), failOnAll VARCHAR(60),  partialThreshPercentage VARCHAR(60),   backInservice VARCHAR(60),  sticky VARCHAR(60),
         retcodeMap VARCHAR(60),   status VARCHAR(60),    created VARCHAR(60),  updated VARCHAR(60), deployed VARCHAR(60));
CREATE INDEX serverfarms_id_idx ON serverfarms (id);

CREATE TABLE predictors( type VARCHAR(60), id VARCHAR(60), name VARCHAR(60), maskType VARCHAR(60), ipNetmask VARCHAR(60), ipv6Prefix VARCHAR(60), beginPattern VARCHAR(60), endPattern VARCHAR(60), length VARCHAR(60), offsetBytes VARCHAR(60),
        cookieName VARCHAR(60), customHeader VARCHAR(60), definedHeader VARCHAR(60), accessTime VARCHAR(60), samples VARCHAR(60), slowStartDur VARCHAR(60), snmpProbe VARCHAR(60), autoAdjust VARCHAR(60), weightConn VARCHAR(60),
        responseType VARCHAR(60), sf_id VARCHAR(60), deployed VARCHAR(60));
CREATE INDEX predictors_id_idx ON predictors (id);

CREATE TABLE rservers(id VARCHAR(60), sf_id VARCHAR(60), name VARCHAR(60),
         type VARCHAR(60), webHostRedir VARCHAR(60),   ipType VARCHAR(60),   address VARCHAR(60),  port VARCHAR(60),  state VARCHAR(60),   opstate VARCHAR(60),    description VARCHAR(60),   failOnAll VARCHAR(60),   minCon INT,  maxCon INT, 
         weight INT,  probes VARCHAR(60), rateBandwidth INT,   rateConnection INT,    redirectionCode VARCHAR(60), backupRS VARCHAR(60),  backupRSport VARCHAR(60),  created VARCHAR(60),  updated VARCHAR(60), cookieStr VARCHAR(60), status VARCHAR(60), adminstatus VARCHAR(60), vm_instance VARCHAR(60), parent_id VARCHAR(60), deployed VARCHAR(60), vm_id VARCHAR(60));
CREATE INDEX rservers_id_idx ON rservers (id);
CREATE INDEX rservers_ip_dep_idx ON rservers (address, deployed);
CREATE INDEX rservers_vm_id_idx ON rservers (vm_id);

CREATE TABLE transactions (id VARCHAR(60), status VARCHAR(60), action VARCHAR(60), params VARCHAR(60));

CREATE TABLE devices (id VARCHAR(60),  name  VARCHAR(60), type VARCHAR(60), version VARCHAR(60), supports_ipv6 INT, requires_vip_ip INT, has_acl INT, supports_vlan INT, ip VARCHAR(60), port VARCHAR(60), 
        user VARCHAR(60), password VARCHAR(60), vip_vlan VARCHAR(60), localpath VARCHAR(60), configfilepath VARCHAR(60), remotepath VARCHAR(60), interface VARCHAR(60), deployed VARCHAR(60), concurrent_deploys VARCHAR(60));

CREATE TABLE vips(id VARCHAR(60), sf_id VARCHAR(60), name VARCHAR(60), ipVersion VARCHAR(60), address VARCHAR(60), mask VARCHAR(60), proto VARCHAR(60), appProto VARCHAR(60), port VARCHAR(60), allVLANs VARCHAR(60), VLAN VARCHAR(60),
        connParameterMap  VARCHAR(60),  KALAPtagName VARCHAR(60),  KALAPprimaryOutOfServ VARCHAR(60),  ICMPreply VARCHAR(60),  status VARCHAR(60),  protocolInspect VARCHAR(60),  appAccelAndOpt VARCHAR(60),
        L7LoadBalancing VARCHAR(60),  lb_id VARCHAR(60),  backupServerFarm VARCHAR(60),  SSLproxyServName VARCHAR(60),  defaultL7LBAction VARCHAR(60),  SSLinitiation VARCHAR(60),  NAT VARCHAR(60),
        created VARCHAR(60),  updated VARCHAR(60), deployed VARCHAR(60));
CREATE INDEX vips_id_idx ON vips (id);

CREATE TABLE vlans(id   VARCHAR(60), description   VARCHAR(60), intType   VARCHAR(60), IPaddr   VARCHAR(60), aliasIPaddr   VARCHAR(60), peerIPaddr   VARCHAR(60), netmask   VARCHAR(60), adminStatus   VARCHAR(60), 
        enableMACsticky   VARCHAR(60), enableNormalization   VARCHAR(60), enableIPv6   VARCHAR(60), ipv6GlobalIP   VARCHAR(60), ipv6UniqueLocalAddr   VARCHAR(60), ipv6LinkLocalAddr   VARCHAR(60), 
        ipv6PeerLinkLocalAddr   VARCHAR(60), enableICMPguard   VARCHAR(60), enableDHCPrelay   VARCHAR(60), RPF   VARCHAR(60), reassemblyTimeout   VARCHAR(60), maxFragChainsAllowed   VARCHAR(60), minFragMTUvalue   VARCHAR(60), 
        MTU   VARCHAR(60), actionForIPheaderOptions   VARCHAR(60), enableMACAddrAutogen   VARCHAR(60), minTTLipHeaderValue   VARCHAR(60), enableSynCookieThreshValue   VARCHAR(60), actionForDBfit   VARCHAR(60), 
        ARPinspectType   VARCHAR(60), UDPconfigCommands   VARCHAR(60), secondaryIPgroups   VARCHAR(60), inputPolicies   VARCHAR(60), inputAccessGroup   VARCHAR(60), outputAccessGroup   VARCHAR(60));

CREATE TABLE probes(sf_id VARCHAR(60),delay VARCHAR(60),attemptsBeforeDeactivation VARCHAR(60),timeout VARCHAR(60), type  VARCHAR(60), id  VARCHAR(60), name  VARCHAR(60), description  VARCHAR(60), probeInterval  VARCHAR(60), passDetectInterval  VARCHAR(60), failDetect  VARCHAR(60), passDetectCount  VARCHAR(60),
        receiveTimeout  VARCHAR(60), isRouted  VARCHAR(60), port  VARCHAR(60), 
        domainName VARCHAR(60), sendData VARCHAR(60), destIP VARCHAR(60), tcpConnTerm VARCHAR(60), openTimeout VARCHAR(60), requestMethodType VARCHAR(60), requestHTTPurl VARCHAR(60), appendPortHostTag VARCHAR(60),
        userName VARCHAR(60), password VARCHAR(60), expectRegExp VARCHAR(60), expectRegExpOffset VARCHAR(60), hash VARCHAR(60), hashString VARCHAR(60), headerName VARCHAR(60), headerValue VARCHAR(60),minExpectStatus VARCHAR(60), 
        maxExpectStatus VARCHAR(60), cipher VARCHAR(60), SSLversion VARCHAR(60),
        maibox VARCHAR(60), requestCommand VARCHAR(60),  userSecret VARCHAR(60), NASIPaddr VARCHAR(60), requareHeaderValue VARCHAR(60), proxyRequareHeaderValue VARCHAR(60), requestURL VARCHAR(60), 
        scriptName VARCHAR(60), scriptArgv VARCHAR(60),  copied VARCHAR(60),  proto VARCHAR(60),  sourceFileName VARCHAR(60),  SNMPComm VARCHAR(60),  SNMPver VARCHAR(60),  maxCPUburstThresh VARCHAR(60), minCPUburstThresh VARCHAR(60),
        maxMemBurstThresh VARCHAR(60), minMemBurstThresh VARCHAR(60), VMControllerName VARCHAR(60), deployed VARCHAR(60));
CREATE INDEX probes_id_idx ON probes (id);
CREATE TABLE stickies(id VARCHAR(60), sf_id VARCHAR(60), name VARCHAR(60), type VARCHAR(60), serverFarm VARCHAR(60), backupServerFarm VARCHAR(60), aggregateState VARCHAR(60), enableStyckyOnBackupSF VARCHAR(60), replicateOnHAPeer VARCHAR(60),
        timeout VARCHAR(60), timeoutActiveConn VARCHAR(60), offset VARCHAR(60), length VARCHAR(60), beginPattern VARCHAR(60), endPattern VARCHAR(60), cookieName VARCHAR(60), enableInsert VARCHAR(60), browserExpire VARCHAR(60), secondaryName VARCHAR(60),
        headerName VARCHAR(60), netmask VARCHAR(60), ipv6PrefixLength VARCHAR(60), addressType VARCHAR(60), prefixLength VARCHAR(60), enableStickyForResponse VARCHAR(60), radiusTypes VARCHAR(60), deployed VARCHAR(60));
CREATE INDEX stickies_id_idx ON stickies (id);

