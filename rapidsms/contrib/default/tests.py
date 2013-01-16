#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf import settings
from rapidsms.tests.harness import EchoApp, RapidTest


class ReturningEchoApp(EchoApp):

    def handle(self, message):
        super(ReturningEchoApp, self).handle(message)
        return True  # Return so that future apps don't handle the message


class DefaultAppTest(RapidTest):
    apps = ['rapidsms.contrib.default']

    def setUp(self):
        if hasattr(settings, 'DEFAULT_RESPONSE'):
            self._default_response = settings.DEFAULT_RESPONSE
        if hasattr(settings, 'PROJECT_NAME'):
            self._project_name = settings.PROJECT_NAME

        self.connection = self.lookup_connections('1112223333')[0]

    def tearDown(self):
        if hasattr(self, '_default_response'):
            settings.DEFAULT_RESPONSE = self._default_response
        elif hasattr(settings, 'DEFAULT_RESPONSE'):
            del settings.DEFAULT_RESPONSE
        if hasattr(self, '_project_name'):
            settings.PROJECT_NAME = self._project_name
        elif hasattr(settings, 'PROJECT_NAME'):
            del settings.PROJECT_NAME

    def test_no_handle(self):
        """App should not respond to message if another has responded."""
        # Add another app & reset the test router.
        self.apps = [ReturningEchoApp, 'rapidsms.contrib.default']
        self.set_router()
        settings.RAPIDSMS_ROUTER = self.router_class

        settings.DEFAULT_RESPONSE = 'hello'
        self.receive('ping', self.connection)
        self.assertEqual(len(self.outbound), 1)
        self.assertNotEqual(self.outbound[0].text, 'hello')

    def test_response_is_none(self):
        """App should not respond if DEFAULT_RESPONSE is None."""
        settings.DEFAULT_RESPONSE = None
        self.receive('asdf', self.connection)
        self.assertEqual(len(self.outbound), 0)

    def test_response_no_project_name(self):
        """App should respond with exact string if project_name is not used."""
        settings.DEFAULT_RESPONSE = 'hello'
        self.receive('asdf', self.connection)
        self.assertEqual(len(self.outbound), 1)
        self.assertEqual(self.outbound[0].text, 'hello')

    def test_response_with_project_name(self):
        """App should replace project_name in response if it is present."""
        settings.DEFAULT_RESPONSE = 'hello %(project_name)s'
        settings.PROJECT_NAME = 'world'
        self.receive('asdf', self.connection)
        self.assertEqual(len(self.outbound), 1)
        self.assertEqual(self.outbound[0].text, 'hello world')
