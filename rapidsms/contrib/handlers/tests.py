#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equal
from rapidsms.conf import settings
from .utils import get_handlers


def test_get_handlers():

    # store current settings.
    _settings = (
        settings.INSTALLED_APPS,
        settings.INSTALLED_HANDLERS,
        settings.EXCLUDED_HANDLERS)

    # clear current settings, to test in a predictable environment.
    settings.INSTALLED_APPS = []
    settings.INSTALLED_HANDLERS = None
    settings.EXCLUDED_HANDLERS = None

    try:
        assert_equal(get_handlers(), [])

        # this crappy test depends upon the ``echo`` contrib app, which
        # defines exactly two handlers. i don't have a cleaner solution.
        settings.INSTALLED_APPS = ['rapidsms.contrib.echo']
        from rapidsms.contrib.echo.handlers.echo import EchoHandler
        from rapidsms.contrib.echo.handlers.ping import PingHandler

        # check that both handlers were found as default
        assert_equal(get_handlers(), [EchoHandler, PingHandler])

        # exclude no handlers, explicitly include a single handler
        settings.INSTALLED_HANDLERS = ['rapidsms.contrib.echo.handlers.ping']
        assert_equal(get_handlers(), [PingHandler])
        settings.INSTALLED_HANDLERS = []

        # exclude a single handler
        settings.EXCLUDED_HANDLERS = ['rapidsms.contrib.echo.handlers.ping']
        assert_equal(get_handlers(), [EchoHandler])

        # exclude all handlers from the echo app
        settings.EXCLUDED_HANDLERS = ['rapidsms.contrib.echo']
        assert_equal(get_handlers(), [])

    # always restore pre-test settings.
    finally:
        settings.INSTALLED_APPS,\
            settings.INSTALLED_HANDLERS,\
            settings.EXCLUDED_HANDLERS = _settings
