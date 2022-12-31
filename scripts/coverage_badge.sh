#!/bin/bash

# small dirty utility script
# creates a pytest coverage badge at /docs/images/coverage.svg


pytest --cov
echo "Creating coverage badge"

# handle if badge already exists
if [ -f ./docs/images/coverage.svg ]; then
    echo "deleting old badge"
    rm ./docs/images/coverage.svg
fi


coverage-badge -o ./docs/images/coverage.svg
echo "Removing .coverage file"
rm .coverage
echo "done"
