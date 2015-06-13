from __future__ import unicode_literals
from six.moves import StringIO

from django.core.management import call_command
from django.test import TestCase


class UpdateAppsAndBackendsTest(TestCase):

    def setUp(self):
        self.output = StringIO()
        # BASE_APPS are needed for the managment commands to load successfully
        self.BASE_APPS = [
            'rapidsms',
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ]

    def test_no_apps_then_none_added(self):
        with self.settings(INSTALLED_APPS=self.BASE_APPS):
            call_command('update_apps', stdout=self.output)
        self.assertEqual(self.output.getvalue(), '')

    def test_adds_app(self):
        # Add an app that has a RapidSMS app
        APPS = self.BASE_APPS + ['rapidsms.contrib.handlers']
        with self.settings(INSTALLED_APPS=APPS):
            call_command('update_apps', stdout=self.output)
        self.assertEqual(self.output.getvalue(), 'Added persistent app rapidsms.contrib.handlers\n')

    def test_no_backends_then_none_added(self):
        with self.settings(INSTALLED_BACKENDS={}):
            call_command('update_backends', stdout=self.output)
        self.assertEqual(self.output.getvalue(), '')

    def test_adds_backend(self):
        INSTALLED_BACKENDS = {
            "message_tester": {"ENGINE": "rapidsms.backends.database.DatabaseBackend"},
        }
        with self.settings(INSTALLED_BACKENDS=INSTALLED_BACKENDS):
            call_command('update_backends', stdout=self.output)
        self.assertEqual(self.output.getvalue(), 'Added persistent backend message_tester\n')
