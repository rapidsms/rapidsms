#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


# import all of the tests in this package, so they're
# all run when this app (rapidsms) (yes, rapidsms is
# a django app now) is tested via './rapidsms test'
from .test_config        import *
from .test_component     import *
from .test_app           import *
from .test_backend       import *
from .test_backend_irc   import *
from .test_backend_spomc import *
from .test_log           import *
#from .test_message       import *
from .test_router        import *


# import a few classes that have doctests attached
# to them, so they're also run via './rapidsms test'
from ..router import Router
from ..app import App

# define which classes to test. this sort of sucks, since they're fun
# via this module, which means that doctest (at least, the _doctest.py
# bundled with django) can't find the line numbers when test fail
__test__ = {
    'Router': Router,
    'App': App
}
