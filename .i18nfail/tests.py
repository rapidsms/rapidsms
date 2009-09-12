#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.test import TestCase
from django.db.models import Manager as BaseManager
from rapidsms.tests.scripted import TestScript
import rapidsms
import app, models


# models


class TestLanguageManager():
    pass


class TestLanguage():
    pass


class TestPersistantAppManager():
    pass


class TestPersistantApp():
    pass


class TestToken():
    pass


class TestString():
    pass


# apps


class TestInternationalApp(TestScript):
    apps = (app.InternationalApp,)


class TestApp(TestScript):
    apps = (app.App,)


    def setUp(self):
        TestScript.setUp(self)

        # disable the magic app spawning during testing, so it's
        # only populated with things that we explicitly create
        models.PersistantApp.objects = models.PersistantApp.raw_objects

        # the only running app (in this
        # test environment) is a mock app
        models.PersistantApp.objects.create(
            title="Mock Application",
            module="apps.mockapp")

        # HACK: overload the "locale" property, which would usually iterate the
        # running apps via rapidsms.settings (which is still available in this
        # testing environment) and create a bunch of objects along the way. to
        # test in isolation, we want known values to be returned. (TODO: this
        # method should be tested separately, in isolation)
        models.PersistantApp.locale = {
            "en": { "greeting": "Hello" },
            "fr": { "greeting": "Bonjour" }}


    def test_language_spawn(self):

        # querying Language.object is enough to populate
        # the table - check that it does so for our mock
        # locale (models.PersistantApp.locale, above)
        lo = models.Language.objects
        self.assertEquals(lo.filter(code="en").count(), 1)
        self.assertEquals(lo.filter(code="fr").count(), 1)
        self.assertEquals(lo.count(), 2)


    test_english="""
        1337 > trans en mockapp greeting
        1337 < apps.mockapp/greeting: Hello [en]"""


    test_french="""
        1337 > trans fr mockapp greeting
        1337 < apps.mockapp/greeting: Bonjour [fr]"""


    test_unknown_app="""
        1337 > trans en XXXXX greeting
        1337 < Unknown app: XXXXX"""


    test_unknown_token="""
        1337 > trans en mockapp XXXXX
        1337 < Unknown token: XXXXX"""


    def test_unknown_language(self):

        # prevent spawning (from the models.PersistantApp.locale stub) during
        # this test, and destroy languages spawned during the previous tests
        models.Language.objects = models.Language.raw_objects
        models.Language.objects.all().delete()

        self.runScript("""
            1337 > trans XXXXX mockapp greeting
            1337 < apps.mockapp/greeting: Hello [en]""")

        # the fallback language (english) should have
        # been spawned when XXXXX could not be found
        self.assertEquals(models.Language.objects.count(), 1)
        self.assertEquals(models.Language.objects.all()[0].code, "en")
