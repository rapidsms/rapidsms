#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from apps.persistance.models import PersistantApp
from apps.i18n.models import Token
from apps.i18n.utils import app_locale


class Command(NoArgsCommand):
    help = "Creates instances of the Token model for all tokens defined."


    def handle_noargs(self, **options):

        # iterate each app, and for
        # those that have a locale...
        for app in PersistantApp.objects.all():
            locale = app_locale(app)
            if locale is not None:

                # unlike Languages, tokens are linked to individual
                # apps. fetch all of the tokens linked to this app
                # that we already have objects for
                known_token_slugs = app.token_set\
                    .values_list("slug", flat=True)

                # create a Token object for each token that exists
                # in the app's locale, but not the database (yet)
                for token_slug in locale.tokens():
                    if not token_slug in known_token_slugs:
                        token = app.token_set.create(slug=token_slug)
                        print "Added token %s" % (token)
