#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import Language, Translation
from apps.reporters.models import PersistantConnection


DEFAULT_LANGUAGE = "en"

def get_language(connection):
    if connection.reporter:
        if connection.reporter.language:
            return connection.reporter.language
    return DEFAULT_LANGUAGE 

def get_translation(string, language_code):
    try:
        lang = Language.objects.get(code=language_code)
        return Translation.objects.get(language=lang, original=string).translation
    except (Language.DoesNotExist, Translation.DoesNotExist):
        return string