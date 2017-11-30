#!/bin/bash

set -x

virtualenv tmpenv
source ./tmpenv/bin/activate
python setup.py develop
cd test
./run_tests.py
exit_status=$?
set +x
echo "exiting with status code $exit_status"
exit $exit_status
