#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
import unittest
import tempfile
from rapidsms import Config

TEST_INI = """
[rapidsms]
apps=app1,app2,app3
backends=backend1

[log]
level=critical
file=/tmp/test.log

[app2]
beginning=yes
end=no

[app3]
type=testapp

[backend1]
type=testbackend
beginning=yes
end=no

"""

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        fd,path = tempfile.mkstemp()
        ini = os.fdopen( fd ,'w' ) 
        ini.write(TEST_INI)
        ini.close()
        self.config = Config(path)

    def test___init__(self):
        pass

    def test_component_section(self):
        cc = self.config.component_section("app1")
        self.assertEqual(cc, {"type": "app1"},
            "default component config incorrect")
        
        cc = self.config.component_section("app2")
        self.assertEqual(cc, {"type": "app2", "beginning": "yes", "end": "no"}, 
            "does not correctly configure component with assumed type var and additional vars")
        
        cc = self.config.component_section("app3")
        self.assertEqual(cc, {"type": "testapp"}, 
            "does not correctly configure component with explicit type variable and no additional vars")
        
        cc = self.config.component_section("backend1")
        self.assertEqual(cc, {"type": "testbackend", "beginning": "yes", "end": "no"}, 
            "does not correctly configure component with explicit type var and additional vars")

    def test_parse_rapidsms_section(self):
        rs = self.config.data["rapidsms"]
        self.assertEqual(type(rs), type({}),
            "function does not return correct type")
        self.assertTrue(rs.has_key("apps"),
            "'rapidsms' section does not contain 'apps' key")
        self.assertTrue(rs.has_key("backends"),
            "'rapidsms' section does not contain 'backends' key")

    def test_parse_log_section(self):
        ls = self.config.data["log"]
        self.assertEqual(ls["level"], "critical",
            "config does not update log level correctly")
        self.assertEqual(ls["file"], "/tmp/test.log",
            "config does not update log file correctly")

    def test___getitem__(self):
        self.assertEquals(type(self.config["rapidsms"]), type({}),
            "config does not return the correct type from __getitem__")

    def test_has_key(self):
        self.assertTrue(self.config.has_key("rapidsms"),
            "config does not have a key that it should have")
        self.assertFalse(self.config.has_key("bogus"),
            "config has a key that it should not have")

    def test___contains__(self):
        self.assertTrue("rapidsms" in self.config, 
            "config does not contain a section that it should")
        self.assertFalse("bogus" in self.config, 
            "config contains a section that it should not have")


if __name__ == "__main__":
    unittest.main()
