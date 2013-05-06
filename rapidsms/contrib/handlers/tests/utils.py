#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase
from django.test.utils import override_settings

from rapidsms.contrib.echo.handlers.echo import EchoHandler
from rapidsms.contrib.echo.handlers.ping import PingHandler
from rapidsms.contrib.handlers.utils import get_handlers

import mock


__all__ = ['TestGetHandlers']


class TestGetHandlers(TestCase):
    DEFAULT_APP = 'rapidsms.contrib.default'  # Defines no handlers
    ECHO_APP = 'rapidsms.contrib.echo'  # Defines exactly 2 handlers
    ECHO_HANDLER = 'rapidsms.contrib.echo.handlers.echo'
    PING_HANDLER = 'rapidsms.contrib.echo.handlers.ping'
    ECHO_HANDLER_CLASS = 'rapidsms.contrib.echo.handlers.echo.EchoHandler'
    PING_HANDLER_CLASS = 'rapidsms.contrib.echo.handlers.ping.PingHandler'

    def setUp(self):
        # Used with override_settings, so that we test in a predictable
        # environment.
        self.settings = {
            'INSTALLED_APPS': [],
            'INSTALLED_HANDLERS': None,
            'EXCLUDED_HANDLERS': [],
            'RAPIDSMS_HANDLERS_EXCLUDE_APPS': [],
        }

    def _check_get_handlers(self, *args):
        with override_settings(**self.settings):
            with mock.patch('rapidsms.contrib.handlers.utils.warn') as warn:
                handlers = get_handlers()
        self.assertEqual(set(handlers), set(args))
        # If RAPIDSMS_HANDLERS is not defined, a deprecation warning is issued
        self.assertEqual(warn.called, 'RAPIDSMS_HANDLERS' not in self.settings)

    def test_no_installed_apps(self):
        """App should not load any handlers if there are no installed apps."""
        self._check_get_handlers()

    def test_no_relevant_installed_apps(self):
        """App should not load any handlers if no app contains handlers."""
        self.settings['INSTALLED_APPS'] = [self.DEFAULT_APP]
        self._check_get_handlers()

    def test_installed_apps(self):
        """App should load handlers from any app in INSTALLED_APPS."""
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self._check_get_handlers(EchoHandler, PingHandler)

    def test_installed_handler__installed_apps(self):
        """
        App should only include handlers listed in INSTALLED_HANDLERS, if it
        is defined.
        """
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['INSTALLED_HANDLERS'] = [self.PING_HANDLER]
        self._check_get_handlers(PingHandler)

    def test_installed_handlers__installed_apps(self):
        """
        App should only include handlers listedin INSTALLED_HANDLERS, if it
        is defined.
        """
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['INSTALLED_HANDLERS'] = [self.PING_HANDLER,
                                               self.ECHO_HANDLER]
        self._check_get_handlers(PingHandler, EchoHandler)

    def test_installed_handlers__no_installed_apps(self):
        """App should handle when an INSTALLED_HANDLER can't be found."""
        self.settings['INSTALLED_HANDLERS'] = [self.PING_HANDLER]
        self._check_get_handlers()

    def test_installed_app(self):
        """App should use prefix matching to determine handlers to include."""
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['INSTALLED_HANDLERS'] = [self.ECHO_APP]
        self._check_get_handlers(EchoHandler, PingHandler)

    def test_exclude_handlers__installed_apps(self):
        """App should exclude handlers listed in EXCLUDED_HANDLERS."""
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['EXCLUDED_HANDLERS'] = [self.PING_HANDLER]
        self._check_get_handlers(EchoHandler)

    def test_exclude_handlers__no_installed_apps(self):
        """App should handle when an EXCLUDED_HANDLER can't be found."""
        self.settings['EXCLUDED_HANDLERS'] = [self.PING_HANDLER]
        self._check_get_handlers()

    def test_exclude_app(self):
        """App should use prefix matching to determine handlers to exclude."""
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['EXCLUDED_HANDLERS'] = [self.ECHO_APP]
        self._check_get_handlers()

    def test_empty_rapidsms_handlers(self):
        # If RAPIDSMS_HANDLERS is empty, no handlers are loaded.
        self.settings['INSTALLED_APPS'] = [self.ECHO_APP]
        self.settings['INSTALLED_HANDLERS'] = [self.ECHO_APP]
        self.settings['RAPIDSMS_HANDLERS'] = []
        self._check_get_handlers()

    def test_rapidsms_handlers(self):
        # If RAPIDSMS_HANDLERS is set, it completely controls which handlers
        # are loaded.
        self.settings['INSTALLED_APPS'] = [self.DEFAULT_APP]
        self.settings['INSTALLED_HANDLERS'] = []
        self.settings['EXCLUDED_HANDLERS'] = [self.PING_HANDLER]
        self.settings['RAPIDSMS_HANDLERS'] = [
            self.ECHO_HANDLER_CLASS,
            self.PING_HANDLER_CLASS
        ]
        self._check_get_handlers(EchoHandler, PingHandler)
