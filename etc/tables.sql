CREATE TABLE loadbalancers(id INT, name TEXT, algorithm TEXT, status TEXT, created TEXT, updated TEXT);
CREATE TABLE serverfarms(id INT, lb_id INT,  name TEXT,
         type TEXT,  description TEXT, failAction TEXT, inbandHealthCheck TEXT, connFailureThreshCount TEXT,  resetTimeout TEXT,   resumeService TEXT,  transparent TEXT, 
         dynamicWorkloadScale TEXT,  vmProbeName TEXT, failOnAll TEXT,  partialThreshPercentage TEXT,   backInservice TEXT,   predictor_id INT,  retcodeMap TEXT,   status TEXT,    created TEXT,
         updated TEXT);
CREATE TABLE predictors( id INT, name TEXT, type TEXT);

CREATE TABLE rservers(id INT,   name TEXT,
         type TEXT, webHostRedir TEXT,   ipType TEXT,   IP TEXT,  port TEXT,  state TEXT,   opstate TEXT,    description TEXT,   failOnAll TEXT,   minCon INT,  maxCon INT, 
         weight INT,  rateBandwidth INT,   rateConn INT,    created TEXT,  updated TEXT);
         

CREATE TABLE transactions (id INT, status TEXT, action TEXT, params TEXT);
