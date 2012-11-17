#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf import settings

from rapidsms.router.test import TestRouter

from rapidsms.tests.harness.base import CreateDataTest
from rapidsms.tests.harness.router import (CustomRouter, MockBackendRouter,
                                           RouterTest, RapidTest,
                                           RapidTransactionTest)
from rapidsms.tests.harness.scripted import TestScript
from rapidsms.tests.harness.backend import MockBackend
from rapidsms.tests.harness.app import MockApp, EchoApp


class setting(object):
    """
    A context manager for the Django settings module that lets you
    override settings while running tests, e.g.:

    with setting(RAPIDSMS_ROUTER='foo.bar.Class'):
        assert_equals(get_router(), foo.bar.Class)
    """

    def __init__(self, **kwargs):
        self.settings = kwargs
        self.saved_settings = {}
        self.default_value = None

    def __enter__(self):
        for k, v in self.settings.items():
            self.saved_settings[k] = getattr(settings, k, self.default_value)
            setattr(settings, k, v)

    def __exit__(self, exc_type, exc_value, traceback):
        for k, v in self.saved_settings.items():
            if v != self.default_value:
                setattr(settings, k, v)


class MockRouter(TestRouter):
    """Legacy support for MockRouter import."""
    pass
