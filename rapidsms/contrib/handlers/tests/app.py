#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.echo.handlers.echo import EchoHandler
from rapidsms.contrib.echo.handlers.ping import PingHandler
from rapidsms.contrib.handlers.app import App as HandlersApp
from rapidsms.contrib.handlers.tests.harness import EchoKeywordHandler
from rapidsms.messages import IncomingMessage
from rapidsms.tests.harness import RapidTest

try:
    from django.test.utils import override_settings
except ImportError:
    from rapidsms.tests.harness import setting as override_settings


__all__ = ['TestHandlersApp']


class TestHandlersApp(RapidTest):

    def setUp(self):
        self.connection = self.create_connection()

    def test_init(self):
        """App should load handlers upon initialization."""
        settings = {
            'INSTALLED_APPS': ['rapidsms.contrib.echo'],  # Defines 2 handlers.
        }
        with override_settings(**settings):
            app = HandlersApp(self.router)
            self.assertEqual(len(app.handlers), 2)
            self.assertTrue(EchoHandler in app.handlers)
            self.assertTrue(PingHandler in app.handlers)

    def test_handle(self):
        """App should call upon its handlers to respond to the message."""
        app = HandlersApp(self.router)
        app.handlers = [EchoKeywordHandler]
        msg = IncomingMessage(self.connection, 'hello world')
        retVal = app.handle(msg)
        self.assertTrue(retVal)
        self.assertEqual(len(msg.responses), 1)
        self.assertEqual(msg.responses[0]['text'], 'world')

    def test_no_handlers(self):
        """If app has no (relevant) handlers, it should return nothing."""
        app = HandlersApp(self.router)
        app.handlers = []
        msg = IncomingMessage(self.connection, 'hello world')
        retVal = app.handle(msg)
        self.assertEqual(retVal, None)
        self.assertEqual(len(msg.responses), 0)
