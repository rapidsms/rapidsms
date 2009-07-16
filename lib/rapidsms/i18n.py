#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
import gettext


#RapidSMS Internationalization (i18n)
# 
# Read more about Django i18n: http://docs.djangoproject.com/en/dev/topics/i18n/
# Read more about Python i18n: http://www.python.org/doc/2.5/lib/node733.html

# path to GNU gettext 'locale' directory
LOCALE_PATH=os.path.join('contrib','locale')

# translation are instantiated globally
_translations = {}
_default = None

# Used to mark sms text that needs to be translated 
from django.utils.translation import ugettext_noop


# ugettext is globally available to make tagging strings easy
def ugettext_from_locale(locale, text):
    """ 
    Used to translate a string given a particulate locale
    
    For example, most modules will import these functions:
        from rapidsms.i18n import ugettext_from_locale as _t
        from rapidsms.i18n import ugettext_noop as _
    '_' will wrap strings that need to be translated for text messages
    '_t' will translate strings given a locale
    For example: 
        response = _t(locale, _("Hello %(name)s!") ) % {"name":name}    
    """
    # TODO: handle mappings from old-style two letter ('en')
    # to new hotness 3-letter codes 'eng'
    global _translations
    translator = _translations[_default].translator
    if locale in _translations:
        translator = _translations[locale].translator
    return translator.ugettext(text)


def init(default='en', languages=[[ 'en','English' ]] ,locale=LOCALE_PATH):
    """ 
    Global initialization function for sms i18n translators
    
    We use the class-based API of GNU Gettext to provide
    multiple dynamic translations
    Do not call this function in runserver, as it will foobar
    the web translations in unpredictable ways.
    
    """
    global _translations, _default
    if not default: default = 'en'
    if not languages: languages = [[ 'en','English' ]]
    for language in languages:
        if language:
            t = _Translation(language[0],language[1:])
            try:
                t.translator = gettext.translation('django',locale,[t.slug,default])
            except IOError, e:
                if str(e).find("No translation file") != -1:
                    raise Exception("Translation file not found. Please create " +
                                    "%s/%s/LC_MESSAGES/django.mo " % (LOCALE_PATH,t.slug) +
                                    "within your project with the correct translations")
                else:
                    raise
            _translations.update ( {t.slug:t} )
    _default = default
    if len(_translations)==1: # if there is only one translation, it's the default
        _default = _translations.keys()[0]
    if _default not in _translations:
        raise Exception("i18n enabled but no default language specified! " +
                        "Please add default_language=<language_code> to rapidsms.ini")

class _Translation(object):
    def __init__(self, slug='', names=[]):
        self.slug = slug
        self.names = names
        self.translator = None


