#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from rapidsms.djangoproject import settings
from persistance.models import PersistantApp
from languages import LANGUAGES
from utils import app_locale


class Language(models.Model):
    """This class represents a single language (obviously) that the SMS strings
       are available in. It isn't related to the WebUI in any way right now. The
       codes are stored as a W3C language tag, which is automatically resolved
       into a description via i18n.languages.LANGUAGES.
       
       The W3C language tag spec:
         http://www.w3.org/International/articles/language-tags/Overview.en.php
       
       The IANA language tag registry reference:
         http://www.iana.org/assignments/language-subtag-registry"""

    code = models.CharField(max_length=10, unique=True)


    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<%s: %s (%s)>' %\
            (type(self).__name__, self.title, self.code)


    @property
    def title(self):
        return LANGUAGES.get(self.code, "Unknown")


    @property
    def fallback(self):
        """Returns the next Language object that a translator should fall back
           to, if a string is not available in this Language. At the moment, all
           Languages fall back to the default, and the default language returns
           None. (This should, obviously, become smarter in future.)"""

        # return the default, so long as this
        # isn't already it (to avoid looping)
        # ORM FAIL: we can't compare _self_ with _default_ directly
        # since django considers them two separate instances. lame.
        default = type(self).default()
        if self.code != default.code:
            return default

        # we have no idea what to
        # fall back to, so abort
        return None

    @classmethod
    def default(cls):
        """Returns the "default" Language object, creating one if none currently
           exist. The default language code is set (as a w3c language tag) in
           the [rapidsms] section of the config, or default to English (en)."""

        # fetch the default language from the conf, or fall
        # back to english, because i don't know any better
        sect = settings.RAPIDSMS_CONF["rapidsms"]
        code = sect.get("default_language", "en")

        # ensure that the language exists
        obj, created = cls.objects.get_or_create(
            code=code)

        # i don't care if it was created
        # or not. just return the object
        return obj


class Token(models.Model):
    """This model represents an individual string that needs translating, that
       can be iterated and listed for some clever bi-lingual person to do. The
       instances are generated after syncdb (or on-demand) by the update_tokens
       command, and generally shouldn't be messed with after that."""

    app  = models.ForeignKey(PersistantApp)
    slug = models.CharField(max_length=30)


    def __unicode__(self):
        return "%s/%s" % (self.app.module, self.slug)

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.slug)


    def translation(self, language):

        # if there is an explicit translation (in the db)
        # for this language+token combo, we're done here
        try:
            return self.string_set.get(
                language=language)

        # it's okay if there's no translation in the database. there
        # should be one in the locale.py, so we'll check there next
        except String.DoesNotExist:
            pass

        # fetch this app's locale. if there isn't one, we'll skip
        # straight to trying the next language - it *is* possible
        # that the strings are _all_ in the database, with no locale
        locale = app_locale(self.app)
        if locale is not None:

            # look for the translation in this app's locale.LOCALE
            # dict. if one was found, wrap it up in a StringStub (to
            # provide the same interface as a real String), and return
            # it (this is useful for checking which language the string
            # ended up in,  since it might have fallen back multiple
            # times). otherwise, we will fall back to the next language
            str = locale.get(
                lang_code=language.code,
                token_slug=self.slug)

            if str is not None:
                return StringStub(
                    language=language,
                    token=self,
                    string=str)

        # if we haven't returned yet, the translation was not found in
        # the database nor locale dict, so we will recurse with the next
        # language. if there are no further languages to try, all we can do
        # is return None to indicate that we have no idea what's going on
        next_lang = language.fallback
        if next_lang is None:
            return None

        # try the next language
        return self.translation(next_lang)


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


class StringStub(object):
    """This class mimics the API of the String model, so it can be passed around
       in the place of a real String, and used without having to worry if the
       translation came from the database or a locale dict.
       
       It is created and returned by the Token.translate method when no "real"
       String instance exists, but a translation was found in a locale dict."""

    def __init__(self, language, token, string):
        self.language = language
        self.token = token
        self.string = string

    def __unicode__(self):
        return self.string

    def __repr__(self):
        return '<%s: %s>' %\
            (type(self).__name__, self.token)


# if the reporters app happens to also be running, we
# can provide some optional integration (see: app.py)
if "reporters" in settings.RAPIDSMS_APPS:
    from reporters.models import Reporter

    class ReporterLanguage(models.Model):
        """This model links a reporter with a language, to indicate that where
           possible, RapidSMS should speak to them in their chosen language. It
           isn't quite as slick as monkey-patching or extending the __bases__ of
           the Reporter class, but the separation allows both apps to optionally
           depend upon one another."""

        reporter = models.OneToOneField(Reporter, primary_key=True)
        language = models.ForeignKey(Language)
