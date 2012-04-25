URL=http://localhost:8181/loadbalancers
#curl -v -H "Content-Type: application/json" -X POST -d@createLBcommand$1 $URL
curl -v -H "Content-Type: application/json" -X POST -d@createLBnewCommand$1 $URL
