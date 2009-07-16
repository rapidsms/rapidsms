import unittest

from rapidsms.manager import Manager, import_local_settings

class TestSettings (object):
    # this class is used by TestManager to test import_local_settings(0
    default = "default"
    overridden = "default"

class TestManager (unittest.TestCase):
    def test_manager (self):
        manager = Manager()
        self.assertTrue(hasattr(manager, "route"))
        self.assertTrue(hasattr(manager, "startproject"))
        self.assertTrue(hasattr(manager, "startapp"))

    def test_local_settings (self):
        settings = TestSettings()
        import_local_settings(settings, __file__, "test_settings.py")
        self.assertEquals(settings.default, "default")
        self.assertEquals(settings.overridden, "overridden")

if __name__ == "__main__":
    unittest.main()
