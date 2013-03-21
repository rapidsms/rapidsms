#!/bin/bash

. ~/VE/rapidsms/bin/activate

coverage run run_tests.py --settings=tests.default
coverage html
