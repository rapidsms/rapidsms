#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.tests.harness import EchoApp, RapidTest

try:
    from django.test.utils import override_settings
except ImportError:
    from rapidsms.tests.harness import setting as override_settings


class ReturningEchoApp(EchoApp):

    def handle(self, message):
        super(ReturningEchoApp, self).handle(message)
        return True  # Return so that future apps don't handle the message


class DefaultAppTest(RapidTest):
    apps = ['rapidsms.contrib.default']

    def setUp(self):
        self.connection = self.lookup_connections('1112223333')[0]

    def test_no_handle(self):
        """App should not respond to message if another has responded."""
        # Add another app & reset the test router.
        self.apps = [ReturningEchoApp, 'rapidsms.contrib.default']
        self.set_router()
        with override_settings(DEFAULT_RESPONSE='hello'):
            self.receive('ping', self.connection)
            self.assertEqual(len(self.outbound), 1)
            self.assertNotEqual(self.outbound[0].text, 'hello')

    def test_response_is_none(self):
        """App should not respond if DEFAULT_RESPONSE is None."""
        with override_settings(DEFAULT_RESPONSE=None):
            self.receive('asdf', self.connection)
            self.assertEqual(len(self.outbound), 0)

    def test_response_no_project_name(self):
        """App should respond with exact string if project_name is not used."""
        with override_settings(DEFAULT_RESPONSE='hello'):
            self.receive('asdf', self.connection)
            self.assertEqual(len(self.outbound), 1)
            self.assertEqual(self.outbound[0].text, 'hello')

    def test_response_with_project_name(self):
        """App should replace project_name in response if it is present."""
        with override_settings(DEFAULT_RESPONSE='hello %(project_name)s',
                               PROJECT_NAME='world'):
            self.receive('asdf', self.connection)
            self.assertEqual(len(self.outbound), 1)
            self.assertEqual(self.outbound[0].text, 'hello world')
