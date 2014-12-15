#!/usr/bin/env python

import sys
import unittest
import all_tests
import logging

try:
    log_level = sys.argv[1].upper()
except:
    log_level = 'WARNING'
logging.basicConfig(level=getattr(logging, log_level))

testSuite = all_tests.create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)
if text_runner.wasSuccessful():
    sys.exit(0)
else:
    sys.exit(1)
