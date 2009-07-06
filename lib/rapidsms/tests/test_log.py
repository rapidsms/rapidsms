#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest, time, logging
from rapidsms.log import Logger
from rapidsms.component import Component
from tempfile import NamedTemporaryFile

expected_output = """
DEBUG [Testing]: this is a debug message: 1
INFO [Testing]: this is a info message: 2
WARNING [Testing]: this is a warning message: 3
ERROR [Testing]: this is a error message: 4
CRITICAL [Testing]: this is a critical message: 5
"""

class TestLog(unittest.TestCase):
    def setUp(self):
        self.tmp = NamedTemporaryFile()

    def test_write (self):
        log = Logger("debug", self.tmp.name, 
                    "%(levelname)s [%(component)s]: %(message)s",
                    False)
        c = Component()
        c._title = "Testing"
        log.write(c, "debug", "this is a debug message: %d", 1) 
        log.write(c, "info", "this is a info message: %d", 2) 
        log.write(c, "warning", "this is a warning message: %d", 3) 
        log.write(c, "error", "this is a error message: %d", 4) 
        log.write(c, "critical", "this is a critical message: %d", 5) 
        self.tmp.flush()
        self.tmp.seek(0)
        output = self.tmp.read()
        self.assertEquals(output, expected_output.lstrip(), "got expected output")

if __name__ == "__main__":
    unittest.main()
