URL=http://localhost:8181/loadbalancers
curl -v -H "Content-Type: application/json" -X POST -d@createLBcommand $URL
