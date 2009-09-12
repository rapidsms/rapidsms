#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from rapidsms.webui import settings
from apps.persistance.models import PersistantApp
from models import Language, Token, String


# is the REPORTERS app running? if so, we'll provide a
# handler for reporters to set their preferred language.
# this app (i18n) is useful without reporters, so i'm
# trying to make this dependancy entirely optional
from rapidsms.webui.settings import RAPIDSMS_APPS
use_reporters = ("i18n" in RAPIDSMS_APPS)
if use_reporters:
    from apps.reporters.models import Reporter
    from models import ReporterLanguage


class InternationalApp(object):
    def _language(self, x):

        # if the argument is already
        # a Language, return it as-is
        if isinstance(x, Language):
            return x

        # if we're integrating with the reporters
        # app, we can accept a lot more things to
        # inspect for a language...
        if use_reporters:

            # if a Reporter was provided, we'll use their chosen
            # language, which is stored way inside ReporterLanguage
            if isinstance(x, Reporter):
                try:
                    return x.reporterlanguage.language

                # if the reporter doesn't have a reporterlanguage associated
                # yet (they're not auto spawned, which sucks), leave this
                # reporter's language as the system default
                except ReporterLanguage.DoesNotExist:
                    return Language.default()

            # if (something that quacks like) a rapidsms.Message
            # extended by the reporters app was provided, pluck
            # out the reporter and recurse to catch it above
            elif hasattr(x, "reporter"):
                return self._language(msg.reporter)

        try:
            # assume that anything else is a language code.
            # some apps might find it useful to hard-code it
            return Language.objects.get(code=x)

        # if the language code was unknown (quite possible if we're
        # resolving a hard-coded string), return None (unknown)
        except (Language.DoesNotExist):
            return None


    def _i18n_string(self, token_slug, lang_code=None):

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
        if lang_code is not None:
            language = self._language(
                lang_code)

            # if the langauage code doesn't exist, (which shouldn't
            # happen, since the code passed to this method should be
            # sourced from previously-validated Language objects),
            # warn and fall back to the system default
            if language is None:
                self.warning(
                    "No such language: %r" %\
                    (lang_code))

                # fall back to the system default.
                # it's better than nothing at all
                language = Language.default()

        # or if the lang_code was omitted,
        # fall back to the system default
        else:
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
            self.warning(
                "No such token: %s" %\
                (token_slug))
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


    def _str(self, token_slug, lang_code=None, *args):

        # fetch the String (or StringStub) via the i18n helper
        # method, which will return in the closest language that
        # it can, and warn if nothing could be found
        string = self._i18n_string(token_slug, lang_code)

        # if *nothing* relevant was found, return the token
        # itself, to at least give the caller some kind of
        # idea what was meant. using the base translation
        # as the key wins here. gettext: 1, adammck: 0.
        if string is None:
            return "{%s}" % (token_slug)

        # we got a string! woo. format it (to replace the
        # placeholders) and return it ready to msg.respond
        return string.string % args




class App(rapidsms.App, InternationalApp):
    SET_LANG_RE = re.compile(r"^(?:speak|language|lang)(?:\s+(.+))?$", re.I)

    def handle(self, msg):

        # if we're integrating with the reporters app, allow
        # reporters to get and set their preferred language
        if use_reporters:
            match = self.SET_LANG_RE.match(msg.text)
            if match is not None:

                # if the caller isn't identified, we don't have anything to
                # attach (or fetch) their preference to (or from), so abort
                # with an error in the system default language
                if not hasattr(msg, "reporter") or msg.reporter is None:
                    msg.respond(self._str("must-identify"))
                    return True

                # if a language code was provided...
                lang_code = match.group(1)
                if lang_code is not None:
                    try:

                        # resolve the language (from the code), and store
                        # it along with the reporter, so future messages
                        # can be transparently internationalized for them
                        lang = Language.objects.get(code__iexact=lang_code)
                        msg.reporter.reporterlanguage = lang
                        msg.reporter.save()

                        # respond with a notification that we will now
                        # (attempt to) communicate in the chosen language
                        msg.respond(self._str(
                            "lang-set",
                            msg.reporter))

                    except Language.DoesNotExist:
                        msg.respond(self._str("invalid-lang"), code=lang_code.upper())

                # if the language was not provided (just the
                # prefix), respond with the current setting
                else:
                    msg.respond(self._str(
                        "lang-reminder",
                        msg.reporter))
