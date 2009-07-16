#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest, threading, time, datetime
#from django.test.client import Client

from rapidsms.i18n import ugettext_from_locale as _t
from rapidsms.i18n import ugettext_noop as _
from rapidsms.i18n import _default
from rapidsms.i18n import init

class TestI18n(unittest.TestCase):
    def setUp(self):
        #self.client = Client()
        pass

    def test_sms(self):
        # this gets cleaned up once rapidsms unit tests are fixed
        init()
        self.assertEquals( _t("You said: %(message)s"), "You said: %(message)s" )

        # this gets cleaned up once rapidsms unit tests are fixed
        init('fr', [ ['en','English'],['fr','Francais'],['de','Deutsche'] ])
        self.assertEquals( _t("You said: %(message)s", 'en'), "You said: %(message)s" )
        self.assertEquals( _t("You said: %(message)s", 'fr'), "Vous avez dit: %(message)s" )
        self.assertEquals( _t("You said: %(message)s", 'de'), "Ni Dichte: %(message)s" )
        # for unknown language codes, revert to default translator
        self.assertEquals( _t("You said: %(message)s", 'ru' ), "Vous avez dit: %(message)s" )

    """ 
    Not sure where to put django-dependent unit tests...
    
    def test_web(self):
        response = self.client.get('')
        self.assertContains(assertContains, "Log in")
        response = self.client.post('i18n/', {'language':'fr'})
        response = self.client.get('')
        self.assertContains(assertContains, "Log in")

    def test_web_and_sms(self):
        # Test together in case of weird initialization dependencies 
        self.test_sms()
        self.test_web()
    """

if __name__ == "__main__":
    unittest.main()
