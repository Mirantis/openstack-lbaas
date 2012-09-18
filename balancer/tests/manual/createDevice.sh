URL=http://localhost:8181/devices
curl -v -H "Content-Type: application/json" -X "POST" -d @createDevice$1 $URL
