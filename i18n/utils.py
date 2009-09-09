#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class Locale(object):
    def __init__(self, src):
        self.src = src

    def languages(self):
        """Returns all of the language codes referenced by this locale. Does not
           include language codes that have been added via the WebUI."""

        if not hasattr(self, "_languages"):
            self._languages = []

            # LOCALE dicts are in the slightly awkward form:
            # { slug: { lang_code: string, lang_code: string } }
            for strings in self.src.values():
                for lang_code in strings.keys():

                    # if this is the first time we've seen
                    # this language code, add it to the cache
                    if lang_code not in self._languages:
                        self._languages.append(lang_code)

        # return the cache, so we don't
        # to generate it every call
        return self._languages

    def tokens(self):
        """Returns all token slugs for this locale, whether or not they have
           been translated in all (or any) languages."""

        return self.src.keys()

    def get(self, token_slug, lang_code):
        """Returns a translation from this locale, or None if the translation
           doesn't exist. Note that both the arguments and return value are
           keys, not Token/Language/String objects."""

        try:
            return self.src[token_slug][lang_code]

        except KeyError:
            return None


def app_locale(persistant_app):
    """Returns a Locale object wrapping the LOCALE dict from a persistant app,
       or None if dict couldn't be imported for whatever reason. Does nothing
       to check the validity of the dict, so be careful."""

    try:
        module_str = "%s.locale" % (persistant_app.module)
        module = __import__(module_str, {}, {}, ["LOCALE"])
        return Locale(module.LOCALE)

    except (ImportError, AttributeError):
        return None
