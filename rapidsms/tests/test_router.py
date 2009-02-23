#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
import helper

import rapidsms.router


class TestRouter(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testfail(self):
        self.assertEqual("a", "b")

    def testwin(self):
        self.assertEqual("c", "c")

if __name__ == "__main__":
    unittest.main()
