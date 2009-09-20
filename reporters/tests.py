#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.tests.scripted import TestScript
#from apps.persistance.app import App as Papp
from app import App


class TestApp (TestScript):
    apps = (App,)

    _testJoining = """
        1111 > JOIN 1234567890
        1111 < blah blah
    """
