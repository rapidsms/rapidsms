from django.test import TestCase
from rapidsms.apps.base import AppBase
from rapidsms.router.blocking import BlockingRouter


class RouterAppTest(TestCase):
    """BlockingRouter app tests."""

    def setUp(self):
        self.router = BlockingRouter(apps=[], backends={})

    def test_valid_app_path(self):
        """Valid RapidSMS app modules should load properly."""
        app = self.router.add_app("rapidsms.contrib.default")
        self.assertTrue(app is not None)
        self.assertEqual(1, len(self.router.apps))

    def test_invalid_app_path(self):
        """Invalid RapidSMS app modules shouldn't raise any errors."""
        app = self.router.add_app('django.conrib.admin')
        self.assertTrue(app is None)

    def test_get_app_by_path(self):
        """get_app() returns loaded app matching the passed module."""
        app1 = self.router.add_app("rapidsms.contrib.default")
        app2 = self.router.get_app("rapidsms.contrib.default")
        self.assertEqual(app1, app2)

    def test_get_invalid_app_by_path(self):
        """get_app() returns None when loaded app is not found."""
        app = self.router.get_app("not.a.valid.app")
        self.assertTrue(app is None)

    def test_add_app_with_class(self):
        """add_app() should also accept a class."""
        self.router.add_app(AppBase)
        self.assertEqual(1, len(self.router.apps))
