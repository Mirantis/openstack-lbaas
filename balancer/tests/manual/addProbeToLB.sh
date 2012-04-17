URL=http://localhost:8181/loadbalancers
curl -X PUT -H "Content-Type: application/json" -d@addProbeCommand $URL/$1/healthMonitoring
