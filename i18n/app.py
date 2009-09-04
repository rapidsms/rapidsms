#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from models import *


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


    def _str(self, language, key, *args, **kwargs):
        lang = self._resolve_language(language)
        str = String.resolve(lang, self, key)
        return str.string.format(*args, **kwargs)


class App(rapidsms.App):
    PATTERN = "^trans\s+(?P<lang_code>\S+)\s+(?P<app_type>\S+)\s+(?P<token_slug>\S+)$"

    def handle(self, msg):

        # abort if this incoming message wasn't
        # for this app. otherwise, parse it crudely
        m = re.match(self.PATTERN, msg.text, re.IGNORECASE)
        if m is None:
            return False

        lang_code, app_type, token_slug = m.groups()

        # if a full module string wasn't provided, assume
        # that the caller meant one in the "apps." module
        # (this will be unnecessary once the patch(es) to
        # add "apps" to the python path from the trunk is
        # merged into this branch)
        if app_type.find(".") == -1:
            app_mod_str = "apps.%s" % (app_type)
        
        # otherwise, use the dotted app_type as-is
        # (for things like rapidsms.contrib.whatever)
        else:
            app_mod_str = app_type

        # return the string in the requested language
        # without formatting - this is just for debugging
        try:
            s = String.resolve(lang_code, app_mod_str, token_slug)
            msg.respond("%s: %s [%s]" % (s.token, s.string, s.language.code))

        except String.UnknownApp:
            msg.respond("Unknown app: %s" % app_type)
        
        except String.NoneExist:
            msg.respond("Unknown token: %s" % token_slug)
