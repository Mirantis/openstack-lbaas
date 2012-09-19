#!/bin/bash

echo "Generation docs..."
cd ../

.venv/bin/sphinx-apidoc -f -o doc/source/apidoc/ balancer
.venv/bin/sphinx-build doc/source/ doc/html/

cd doc/
echo "Done."