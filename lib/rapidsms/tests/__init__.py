#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, doctest


def suite():
    """
    Returns an extended test suite for this module, which includes all of the
    test modules in this package (rapidsms.tests), along with important parts of
    RapidSMS which aren't usually tested. (Django only runs tests declared in
    models.py and tests.py as default. imported modules are ignored.)
    """

    # run all of the tests in this directory
    from . import test_config
    from . import test_component
    from . import test_backend
    from . import test_backend_irc
    from . import test_app
    from . import test_log
    #from . import test_message
    from . import test_router

    # import various other modules,
    # to find and run their doctests
    from .. import router, app

    # start with an empty test suite
    _suite = unittest.TestSuite()

    # iterate all of the modules that we
    # just imported, looking for tests
    l = locals().copy()
    for name in l:

        # ignore privates
        if name.startswith("_"):
            continue

        # load regular unit tests from 'name'
        _suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(
            l[name]))

        # check for doctests, too. ValueError is
        # raised if none are found; no big deal
        try:
            _suite.addTest(doctest.DocTestSuite(
                l[name]))

        except ValueError:
            pass

    return _suite
