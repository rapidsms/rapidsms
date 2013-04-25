#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase, TransactionTestCase

from rapidsms.router.test import TestRouter

from rapidsms.tests.harness.base import CreateDataMixin, LoginMixin
from rapidsms.tests.harness.router import (CustomRouterMixin, TestRouterMixin,
                                           DatabaseBackendMixin)
from rapidsms.tests.harness.scripted import TestScriptMixin
from rapidsms.tests.harness.backend import MockBackend, RaisesBackend
from rapidsms.tests.harness.app import MockApp, EchoApp, ExceptionApp


class RapidTest(TestRouterMixin, LoginMixin, TestCase):
    pass


class RapidTransactionTest(TestRouterMixin,  LoginMixin, TransactionTestCase):
    pass


class TestScript(TestScriptMixin, TestCase):
    pass


class MockRouter(TestRouter):
    """Legacy support for MockRouter import."""
    pass
