#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from apps.persistance.models import PersistantApp
from models import Language, Token, String


class InternationalApp(rapidsms.App):
    def _resolve_language(self, x):

        # if (something that quacks like) a Reporter was provided,
        # we'll use their chosen language. note: it might be blank
        # or null, in which case, we'll fall back later
        if hasattr(x, "language"):
            return x.language

        # if (something that quacks like) a rapidsms.Message
        # extended by the reporters app was provided, pluck
        # out the associated language
        elif hasattr(x, "reporter"):
            return x.reporter.language

        # assume that anything else can quack like a
        # string, and be evaluated as a language code
        return x


    def _i18n_string(self, lang_code, token_slug):

        # fetch the persistant app object for this
        # app, since the tokens are linked to it
        persistant_app = PersistantApp.resolve(self)
        if persistant_app is None:

            # this shouldn't ever happen, so log and abort
            self.warning("PersistantApp does not exist")
            return None

        # we accept a few different language-aware
        # objects, so resolve this elsewhere. the
        # output is always a language code
        #language = Language.objects.get(
        #    code=self._language(lang))
        try:
            language = Language.objects.get(
                code=lang_code)

        # if the langauage code doesn't exist, (which shouldn't
        # happen, since the code passed to this method should be
        # sourced from previously-validated Language objects),
        # warn and fall back to the system default
        except Language.DoesNotExist:
            self.warning(
                "No such language: %s" %\
                (lang_code))

            # fall back to the system default.
            # it's better than nothing at all
            language = Language.default()

        # fetch the token object via its slug,
        # which should be defined in locale.py
        try:
            token = persistant_app.token_set.get(
                slug=token_slug)

        # token objects don't auto-spawn any more, so this
        # could happen because of a typo or something. warn,
        # but let the calling method deal with it
        except Token.DoesNotExist:
            self.warning("No such token: %s" % (token_slug))
            return None

        # attempt to fetch the translation of the token in the
        # requested language, and warn/abort if none were found
        string = token.translation(language)
        if string is None:
            self.warning(
                "No strings for token: %s in language: %s (or fallbacks)" %\
                (token_slug, lang_code))
            return None

        return string


    def _str(self, lang_code, token_slug, *args, **kwargs):

        # fetch the String (or StringStub) via the i18n helper
        # method, which will return in the closest language that
        # it can, and warn if nothing could be found
        string = self._i18n_string(lang_code, token_slug)

        # if *nothing* relevant was found, return the token
        # itself, to at least give the caller some kind of
        # idea what was meant. using the base translation
        # as the key wins here. gettext: 1, adammck: 0.
        if string is None:
            return "{%s}" % (token_slug)

        # we got a string! woo. format it (to replace the
        # placeholders) and return it ready to msg.respond
        return string.string.format(*args, **kwargs)




class App(InternationalApp):
    def handle(self, msg):
        msg.respond(self._str("de", "monkey"))
        return True
