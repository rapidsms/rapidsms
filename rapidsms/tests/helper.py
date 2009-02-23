#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys, os

# since we're running unit tests from the "rapidsms/tests"
# directory (relative to the repository root), patch the
# python path to include the grandparent ("../../"). this
# enables us to import specific parts of rapidsms using the
# same name as we would outside of the testing environment:
#
#   # unit testing support
#   import unittest
#   import helper
#   
#   # just the router for testing
#   import rapidsms.router

dir, file = os.path.split(__file__)
rapidsms_root = "%s/../.." % (dir)
sys.path.append(rapidsms_root)
