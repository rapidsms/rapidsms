import unittest
import os

from rapidsms.manager import Manager, import_local_settings
from rapidsms.manager import import_i18n_web_settings
from rapidsms.manager import import_i18n_sms_settings
from rapidsms.config import Config
from django.conf import settings
import rapidsms.i18n as i18n

class TestSettings (object):
    # this class is used by TestManager to test import_local_settings(0
    default = "default"
    overridden = "default"
    LANGUAGE_CODE = "en-us"
    LANGUAGES = ( range(0,45) )

class TestManager (unittest.TestCase):
    def setUp(self):
        # must ensure the various dependencies for  
        # django.conf.settins are set up properly
        os.environ["RAPIDSMS_INI"] = "rapidsms.ini"
        from rapidsms.webui import settings
        from django.core.management import setup_environ
        setup_environ(settings)
        self.settings = settings
        self.manager = Manager()
        self.conf = {}
        i18n._translations = {}
        i18n._default = None
        
    def test_manager (self):
        self.assertTrue(hasattr(self.manager, "route"))
        self.assertTrue(hasattr(self.manager, "startproject"))
        self.assertTrue(hasattr(self.manager, "startapp"))

    def test_local_settings (self):
        settings = TestSettings()
        import_local_settings(settings, __file__, "test_settings.py")
        self.assertEquals(settings.default, "default")
        self.assertEquals(settings.overridden, "overridden")

    def test_i18n_web_settings_1 (self):
        import_i18n_web_settings(self.settings, self.conf)
        self.assertFalse( hasattr(self.settings,"RAPIDSMS_I18N") )
        self.assertEquals( settings.LANGUAGE_CODE, "en-us")
        # django's got some ridiculous number of built-in languages
        self.assertTrue( len(settings.LANGUAGES)>45 )

    def test_i18n_web_settings_2 (self):
        self.conf["i18n"] = {}
        import_i18n_web_settings(self.settings, self.conf)
        self.assertEquals(self.settings.RAPIDSMS_I18N, True)
        self.assertEquals(settings.LANGUAGE_CODE, "en-us")
        self.assertTrue( len(settings.LANGUAGES)>45 )

    def test_i18n_web_settings_3 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["default_language"] = 'fr'
        import_i18n_web_settings(self.settings, self.conf)
        self.assertEquals(self.settings.RAPIDSMS_I18N, True)
        self.assertEquals(settings.LANGUAGE_CODE, 'fr')
        self.assertTrue( len(settings.LANGUAGES)>45 )

    def test_i18n_web_settings_4 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["languages"] = [ ['de','deutsche'],['fr','francais','french'] ]
        os.environ["DJANGO_SETTINGS_MODULE"] = "rapidsms.webui.settings"
        import_i18n_web_settings(self.settings, self.conf)
        self.assertEquals( self.settings.RAPIDSMS_I18N, True )
        self.assertEquals( settings.LANGUAGES, ( ('de','deutsche'),('fr','francais') ) )
        
    def test_i18n_web_settings_5 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["languages"] = [ ['de','deutsche'],['fr','francais','french'] ]
        self.conf["i18n"]["web_languages"] = [ ['ki','Klingon'],['elf','Elvish','Yiddish'] ]
        os.environ["DJANGO_SETTINGS_MODULE"] = "rapidsms.webui.settings"
        import_i18n_web_settings(self.settings, self.conf)
        self.assertEquals(self.settings.RAPIDSMS_I18N, True)
        self.assertEquals( settings.LANGUAGES, ( ('ki','Klingon'),('elf','Elvish') ) )

    def test_i18n_sms_settings_1 (self):
        import_i18n_sms_settings(self.conf)
        self.assertEquals( i18n._default, None )
        self.assertEquals( len(i18n._translations),0 )

    def test_i18n_sms_settings_2 (self):
        self.conf["i18n"] = {}
        import_i18n_sms_settings(self.conf)
        self.assertEquals( i18n._default, "en")
        self.assertTrue( "en" in i18n._translations )
        self.assertEquals( len(i18n._translations),1 )

    def test_i18n_sms_settings_3 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["default_language"] = 'fr'
        import_i18n_sms_settings(self.conf)
        self.assertEquals( i18n._default, 'fr' )
        self.assertTrue( "fr" in i18n._translations )
        self.assertEquals( len(i18n._translations),1 )

    def test_i18n_sms_settings_4 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["languages"] = [ ['de','deutsche'],['fr','francais','french'] ]
        # pass a set of languages without specifying a default
        self.failUnlessRaises( Exception, import_i18n_sms_settings, self.conf )

    def test_i18n_sms_settings_5 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["default_language"] = 'kli'
        self.conf["i18n"]["languages"] = [ ['de','deutsche'],['fr','francais','french'] ]
        # default language not in languages
        self.failUnlessRaises( Exception, import_i18n_web_settings, self.conf )
        
    def test_i18n_sms_settings_6 (self):
        self.conf["i18n"] = {}
        self.conf["i18n"]["default_language"] = 'ki'
        self.conf["i18n"]["languages"] = [ ['de','deutsche'],['fr','francais','french'] ]
        self.conf["i18n"]["sms_languages"] = [ ['ki','Klingon'],['elf','Elvish','Yiddish'] ]
        import_i18n_sms_settings(self.conf)
        self.assertEquals( i18n._default, 'ki' )
        self.assertTrue( "ki" in i18n._translations )
        self.assertTrue( "elf" in i18n._translations )
        self.assertEquals( len(i18n._translations),2 )

if __name__ == "__main__":
    unittest.main()
