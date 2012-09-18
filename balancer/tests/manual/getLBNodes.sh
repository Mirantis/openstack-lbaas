URL=http://localhost:8181/foo/loadbalancers
curl -X GET -H "Content-Type: application/json" $URL/$1/nodes
