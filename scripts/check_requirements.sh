#!/bin/bash


# This script is used to make sure the project requirements.txt file is up to date
# Intended to be used as a pre-commit hook, hook written in .pre-commit-config.yaml
# sourced from : https://github.com/edkrueger/poetry-package-template-gemfury/blob/main/write_requirements.sh

FAILED=false


# requirements
NEW_REQUIREMENTS=$(poetry export -f requirements.txt --without-hashes --with dev)

# handle if requirements.txt doesn't exist
if [ -f requirements.txt ]; then
    echo "requirements.txt exists!"
else
    echo "FAILURE: requirements.txt does not exist!"
    poetry export --format requirements.txt --output requirements.txt --without-hashes --with dev
    FAILED=True
fi

REQUIREMENTS=$(cat requirements.txt)

# handle if requirements.txt is up to date
if [ "$NEW_REQUIREMENTS" = "$REQUIREMENTS" ]; then
    echo "requirements.txt is up to date!"
else
    echo "FAILURE: requirements.txt is not up to date!"
    poetry export --format requirements.txt --output requirements.txt --without-hashes --with dev
    FAILED=True
fi

echo $FAILED
# handle exit
if [ "$FAILED" = true ]; then
    exit 1
fi
exit 0
