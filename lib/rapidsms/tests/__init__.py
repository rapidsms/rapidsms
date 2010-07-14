#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest, doctest


def suite():
    """
    Return a test suite for this module, which includes all of the test
    modules in this package (rapidsms.tests), along with the important
    parts of RapidSMS which aren't found automatically. (Django only
    runs tests declared in models.py and tests.py as default.)
    """

    # import various other modules,
    # to find and run their doctests
    from ..         import router
    from ..log      import mixin
    from ..apps     import base
    from ..backends import base
    from ..messages import base, incoming, outgoing, error

    from ..utils import modules

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
