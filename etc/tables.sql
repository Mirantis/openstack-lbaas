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

CREATE TABLE vips(id INT, ip_type TEXT, ip_addr TEXT, transport_proto TEXT, app_proto TEXT, port INT, vlan INT, sf_id INT, backup_sf_id INT);
