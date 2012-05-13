URL=http://localhost:8181/loadbalancers
for ((i=2; i<40; i++)) do
	sed "s/%IP%/$i/g" createLBcommand > createLB$i
	curl -v -H "Content-Type: application/json" -X POST -d@createLB$i $URL
	sleep 1
	#head -n 20 createLB$i
done
