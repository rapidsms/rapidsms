#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from rapidsms.webui import settings
import rapidsms




class LanguageManager(models.Manager):
    def get_query_set(self):

        # fetch a list of all the language codes that
        # we already have objects for. this will almost
        # always be the same, but we're not caching yet
        known_lang_codes = Language.raw_objects.values_list("code", flat=True)

        # iterate the LOCALE dict of every known app,
        # and create a Language object for each unknown
        # language code that we encounter
        for app in PersistantApp.objects.all():
            try:

                # LOCALE dicts are in the slightly awkward form:
                # { slug: { lang_code: string, lang_code: string } }
                for strings in app.locale.values():
                    for lang_code in strings.keys():
                        
                        # if this language code isn't in the database,
                        # add it - even if it's only used in a single
                        # place, we need it to link the Token and String
                        if not lang_code in known_lang_codes:
                            Language.raw_objects.create(
                                code=lang_code)

            # app.locale raises import error for apps
            # that don't have a locale.py. no big deal
            except ImportError:
                pass

        # now that we're sure the language table is up
        # to date, continue fetching the queryset as usual
        return super(LanguageManager, self).get_query_set()




class Language(models.Model):
    """This class represents a single language (obviously) that the SMS strings
       are available in. It isn't related to the WebUI in any way right now. The
       instances are kept up to date by LangaugeManager, and generally shouldn't
       be manually created or deleted."""

    title = models.CharField(max_length=30, blank=True)

    # the language code as a w3c language tag
    #   the spec:  http://www.w3.org/International/articles/language-tags/Overview.en.php
    #   reference: http://www.iana.org/assignments/language-subtag-registry
    code = models.CharField(max_length=10, unique=True)

    raw_objects = models.Manager()
    objects = LanguageManager()


    def __unicode__(self):
        return self.title or "[%s]" % self.code.upper()

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self)


    @classmethod
    def default(cls):
        """Returns the "default" Language object, creating one if none currently
           exist. The default language code is set (as a w3c language tag) in the
           [rapidsms] section of the config, or default to English (en)."""

        code = settings.RAPIDSMS_CONF["rapidsms"].get(
            "default_language", "en")

        obj, created = cls.objects.get_or_create(code=code)
        return obj




class PersistantAppManager(models.Manager):
    def get_query_set(self):

        # fetch a list of all the apps
        # that we already have objects for
        known_apps = PersistantApp.raw_objects.values_list("module", flat=True)

        # find any running apps which currently
        # don't have objects, and fill in the gaps
        for conf in settings.RAPIDSMS_APPS.values():
            module = conf["module"]
            
            if not module in known_apps:
                PersistantApp.raw_objects.create(
                    title=conf["title"],
                    module=module)

        # now that we're sure the persistantapp table is up
        # to date, continue fetching the queryset as usual
        return super(PersistantAppManager, self).get_query_set()




class PersistantApp(models.Model):
    """This class exists to allow other models in this module to link themselves
       to an app, without resorting to storing module strings themselves. The
       Django ContentType stuff doesn't work here, since not all RapidSMS apps
       are valid Django apps; but we still need instances here.
       
       Instances of this model are created automatically by the PersistantAppManager
       class on demand, so even when the database is empty, PersistantApp.objects.all()
       can still be used to iterate the running apps.
       
       At some point later on, it might be nice to move this model (along with
       PersistantConnection and PersistantBackend) to the RapidSMS contrib apps."""

    title  = models.CharField(max_length=30, blank=True)
    module = models.CharField(max_length=30, unique=True)

    raw_objects = models.Manager()
    objects = PersistantAppManager()


    class Meta:
        verbose_name = "App"


    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.module)


    @property
    def locale(self):
        """Returns the LOCALE dict from this app's locale.py, or raises ImportError
           if none exists. Does nothing to check the validity of the dict (oops)."""

    @property
    def tokens(self):
        try:
            return [
                Token.LocaleTokenStub(self, slug)
                for slug in self.locale.keys()]
        
        # if this app doesn't have a locale, it obviously
        # won't contain any strings to translate, so return
        # an empty list to iterate (or not) through
        except ImportError:
            return []



class Token(models.Model):
    """This model represents an individual string that needs translating, that
       can be iterated and listed for some clever bi-lingual person to do. The
       instances aren't auto-populated like other models in this module, since
       there's no canoncial list of the tokens for apps."""

    app  = models.ForeignKey(PersistantApp)
    slug = models.CharField(max_length=30)
    help = models.TextField()


    def __unicode__(self):
        return "%s/%s" % (self.app.module, self.slug)

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.slug)


    class LocaleTokenStub(object):
        def __init__(self, app, slug):
            self.app = app
            self.slug = slug




class String(models.Model):
    """This model represents a single translation of a token. The _resolve_
       method is the easiest way to look up a string in an arbitrary language,
       and manages the lookup and fall-back when strings aren't available."""

    language = models.ForeignKey(Language)
    token    = models.ForeignKey(Token)
    string   = models.TextField()


    def __unicode__(self):
        return self.string

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.token)


    class UnknownApp(PersistantApp.DoesNotExist):
        pass


    class NoneExist(models.ObjectDoesNotExist):
        """Like String.DoesNotExist, except multiple Strings and LOCALE files
           have been searched, and no valid string was found in any of them."""

        pass


    class LocaleStringStub(object):
        """This class mimics the API of the String model, so it can be passed
           around in the place of a real String. It is created and returned by
           the String.resolve model when no "real" String instance exists, but
           a translation was found in a locale.py"""

        def __init__(self, language, token, string):
            self.language = language
            self.token = token
            self.string = string

        def __unicode__(self):
            return self.string


    @classmethod
    def resolve(cls, lang, app, token):
        """Returns a translated string, ready to be formatted and returned to
           an end-user... by any means necessary. The arguments can be provided
           in a variety of ways (to make calling this method as unobtrusive as
           possible), like so:

             lang: a Language object, or W3C language code

             app: a PersistantApp object, a rapidsms.App object, or the full
                  module string of a running RapidSMS app.

             token: a Token object, or a slug to be looked up via Token.slug.
                    if no token currently exists for the given app+slug combo,
                    it will be created automatically.

            The translations returned by this method are stored in a variety of
            places, none of which are GNU gettext. It would be nice to introduce
            support for that, but I'm not going to do it, because the notion of
            using the source translations as the keys makes me gag, and the
            entire toolchain seems to be designed for C programmers from 1970.
            Anyhoo, this method checks, in order:

              [1] an Instance of String with matching lang+app+token

              [2] the apps locale.LOCALE[lang][token] (see i18n.locale for an
                  example of this. it's just a nested dict)

              [3] an Instance of String with matching app+token, and the system
                  fallback language (see Language.default -- it's configurable
                  via the RapidSMS ini, or defaults to English)

              [4] the apps locale.LOCALE with the fallback language

              [5] BOOM. raises String.NoneExist.

            Since this entire module deals exclusively with internationalized
            SMS messages (not the Django WebUI), this method will usually be
            called from a subclass of rapidsms.App -- in those cases, take a
            look at apps.i18n.app.InternationalApp, which wraps calls to this
            method in a _str utility method."""

        # resolve the language into an object, or fall back to the
        # system default. LanguageManager keeps the table up to date
        # automatically, so _lang_ has to be unknown (in locale.py
        # and the database) for this to fall back
        if not isinstance(lang, Language):
            try:
                lang = Language.objects.get(
                    code=lang.lower())

            except Language.DoesNotExist:
                lang = Language.default()



        # all tokens should be pre-declared in locale.py files,
        # but there are probably situations where they won't be,
        # so allow Tokens to be created dynamically
        if not isinstance(token, Token):
            token, created = Token.objects.get_or_create(
                app=app, slug=token)

        # if there is an explicit translation (in the db)
        # for this language+token combo, we're done here
        try:
            return cls.objects.get(
                language=lang,
                token=token)

        # oh dear. nobody has translated this combo. we'll
        # look in the app's locale.py next, for the default
        except cls.DoesNotExist:

            # find the LOCALE constant via the config, since apps can be
            # loaded via arbitrary module strings now (apps.whatever vs
            # rapidsms.apps.whatever vs rapidsms.contrib.apps.whatever)
            try:
                str = app.locale[token.slug][lang.code]

            # oh no! this app doesn't have a LOCALE, or the combo isn't
            # included. that shouldn't happen. start over again with the
            # next fallback language
            except (ImportError, KeyError):
                if lang != Language.default():
                    return cls.resolve(Language.default(), app, token)

                # we have exhausted all possibilities. there is no entry
                # in the db or locale.py for this combo, for the requested
                # language OR the system default!
                raise cls.NoneExist(
                    "Couldn't resolve %r into a %s or LocaleStringStub" %\
                        (token, cls.__name__))

            # we found the string in a LOCALE. wrap it up in a stub class, so
            # it can be handled in exactly the same way as a real String object
            # would (useful for checking which language the string ended up in,
            # since it might have fallen back to default(s))
            return cls.LocaleStringStub(lang, token, str)
