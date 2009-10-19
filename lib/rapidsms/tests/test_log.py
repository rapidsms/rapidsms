#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest
from rapidsms.log import Logger
from rapidsms.app import App as AppBase
from tempfile import NamedTemporaryFile


EXPECTED_OUTPUT = """
DEBUG [Testing]: this is a debug message: 1
INFO [Testing]: this is a info message: 2
WARNING [Testing]: this is a warning message: 3
ERROR [Testing]: this is a error message: 4
CRITICAL [Testing]: this is a critical message: 5
""".lstrip()


class MockApp(AppBase):
    _title = "Testing"


class TestLog(unittest.TestCase):
    def setUp(self):
        self.tmp = NamedTemporaryFile()
        self.app = MockApp()

    def tearDown(self):
        self.tmp.close()

    def test_write (self):
        log = Logger("debug", self.tmp.name, 
                    "%(levelname)s [%(component)s]: %(message)s",
                    False)

        log.write(self.app, "debug", "this is a debug message: %d", 1)
        log.write(self.app, "info", "this is a info message: %d", 2)
        log.write(self.app, "warning", "this is a warning message: %d", 3)
        log.write(self.app, "error", "this is a error message: %d", 4)
        log.write(self.app, "critical", "this is a critical message: %d", 5)

        # fetch the contents of the mock log file that
        # was created in response to the events above
        self.tmp.flush()
        self.tmp.seek(0)
        output = self.tmp.read()

        self.assertEquals(output, EXPECTED_OUTPUT)
