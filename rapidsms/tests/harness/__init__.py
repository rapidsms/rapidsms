#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.test import TestCase, TransactionTestCase

from rapidsms.router.test import TestRouter
from rapidsms.tests.harness.base import LoginMixin
from rapidsms.tests.harness.router import TestRouterMixin
from rapidsms.tests.harness.scripted import TestScriptMixin


class RapidTest(TestRouterMixin, LoginMixin, TestCase):
    """
    Inherits from :py:class:`~rapidsms.tests.harness.TestRouterMixin`,
    :py:class:`~rapidsms.tests.harness.LoginMixin`,
    :py:class:`~django.test.TestCase`.
    """

    pass


class RapidTransactionTest(TestRouterMixin, LoginMixin, TransactionTestCase):
    """
    Inherits from :py:class:`~rapidsms.tests.harness.TestRouterMixin`,
    :py:class:`~rapidsms.tests.harness.LoginMixin`,
    :py:class:`~django.test.TransactionTestCase`.
    """

    pass


class TestScript(TestScriptMixin, TestCase):
    """
    Inherits from :py:class:`~rapidsms.tests.harness.TestScriptMixin`,
    :py:class:`~django.test.TransactionTestCase`.
    """

    pass


class MockRouter(TestRouter):
    """Legacy support for MockRouter import."""

    pass
