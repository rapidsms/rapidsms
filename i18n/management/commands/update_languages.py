#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from apps.persistance.models import PersistantApp
from apps.i18n.models import Language
from apps.i18n.utils import app_locale


class Command(NoArgsCommand):
    help = "Creates instances of the Language model for all languages in use."


    def handle_noargs(self, **options):

        # fetch all of the language codes
        # that we already have objects for
        known_lang_codes = Language.objects\
            .values_list("code", flat=True)

        # iterate each app, and for
        # those that have a locale...
        for app in PersistantApp.objects.all():
            locale = app_locale(app)
            if locale is not None:

                # create a Language object for each language that
                # is present in this locale, but not the database
                for lang_code in locale.languages():
                    if not lang_code in known_lang_codes:
                        lang = Language.objects.create(code=lang_code)
                        print "Added language %s" % lang
