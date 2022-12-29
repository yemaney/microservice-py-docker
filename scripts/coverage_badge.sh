#!/bin/bash

# small dirty utility script
# creates a pytest coverage badge at /docs/images/coverage.svg


pytest --cov
echo "Creating coverage badge"
coverage-badge -o ./docs/images/coverage.svg
echo "Removing .coverage file"
rm .coverage
echo "done"
