user=test
password=swordfish
curl  -d '{"auth":{"passwordCredentials":{"username": "test", "password": "swordfish"}, "tenantName": "LBServiceTest001"}}' -H "Content-type: application/json" http://localhost:5000/v2.0/tokens

echo "Auth"
curl  -d '{"auth":{"passwordCredentials":{"username": "admin", "password": "swordfish"}}}' -H "Content-type: application/json" http://localhost:5000/v2.0/tokens
