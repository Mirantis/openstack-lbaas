#!/bin/bash

URL=http://localhost:8181/foo/loadbalancers
curl -v -H "Content-Type: application/json" -X POST -d@createLBcommand$1 $URL
