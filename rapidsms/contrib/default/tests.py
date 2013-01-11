#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf import settings
from django.test.utils import override_settings
from rapidsms.tests.harness import RapidTest
from rapidsms.tests.harness import EchoApp


class ReturningEchoApp(EchoApp):

    def handle(self, message):
        super(ReturningEchoApp, self).handle(message)
        return True  # Return so that future apps don't handle the message


class DefaultAppTest(RapidTest):
    apps = ['rapidsms.contrib.default']

    def receive(self, text, connection=None, fields=None):
        connection = connection or self.lookup_connections('1112223333')[0]
        return super(DefaultAppTest, self).receive(text, connection, fields)

    @override_settings(DEFAULT_RESPONSE='hello')
    def test_no_handle(self):
        """App should not respond to message if another has responded."""
        # Add another app & reset the test router.
        self.apps = [ReturningEchoApp, 'rapidsms.contrib.default']
        self.set_router()
        setattr(settings, 'RAPIDSMS_ROUTER', self.router_class)

        self.receive('ping')
        self.assertEqual(len(self.outbound), 1)
        self.assertNotEqual(self.outbound[0].text, 'hello')

    @override_settings(DEFAULT_RESPONSE=None)
    def test_response_is_none(self):
        """App should not respond if DEFAULT_RESPONSE is None."""
        self.receive('asdf')
        self.assertEqual(len(self.outbound), 0)

    @override_settings(DEFAULT_RESPONSE='hello')
    def test_response_no_project_name(self):
        """App should respond with exact string if project_name is not used."""
        self.receive('asdf')
        self.assertEqual(len(self.outbound), 1)
        self.assertEqual(self.outbound[0].text, 'hello')

    @override_settings(DEFAULT_RESPONSE='hello %(project_name)s',
                       PROJECT_NAME='world')
    def test_response_with_project_name(self):
        """App should replace project_name in response if it is present."""
        self.receive('asdf')
        self.assertEqual(len(self.outbound), 1)
        self.assertEqual(self.outbound[0].text, 'hello world')
