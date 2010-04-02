#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, doctest
from rapidsms.conf import settings
from .utils import find_handlers


def suite():
    """
    Test the handlers of all installed RapidSMS apps using doctests.
    """

    _suite = unittest.TestSuite()

    for module_name in settings.INSTALLED_APPS:
        for handler in find_handlers(module_name):
            try:
                _suite.addTest(doctest.DocTestSuite(
                    handler.__module__))

            except ValueError:
                pass

    return _suite
