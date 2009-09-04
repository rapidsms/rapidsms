#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import Language, Translation
from reporters.models import PersistantConnection
import re

DEFAULT_LANGUAGE = "en"

def get_language_code(connection):
    if connection.reporter:
        if connection.reporter.language:
            return connection.reporter.language
    return DEFAULT_LANGUAGE 

def get_language_from_code(language_code):
    languages = Language.objects.all()
    for language in languages:
        if re.match(language.pattern.regex, language_code, re.IGNORECASE):
            return language
    if language_code == DEFAULT_LANGUAGE:
        # so we don't infinite loop
        return None
    return get_language_from_code(DEFAULT_LANGUAGE)

def get_translation(string, language_code):
    try:
        language = get_language_from_code(language_code)
        if language:
            return Translation.objects.get(language=language, original=string).translation
    except Translation.DoesNotExist:
        # hopefully the default passed in string will work
        pass
    return string