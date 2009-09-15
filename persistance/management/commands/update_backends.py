#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from persistance.models import PersistantBackend
from rapidsms.djangoproject import settings


class Command(NoArgsCommand):
    help = "Creates instances of the PersistantBackend model for all running apps."


    def handle_noargs(self, **options):

        # fetch all of the backends (identified
        # by their slug, which is unique and url-
        # friendly) that we already have objects for
        known_backend_slugs = list(PersistantBackend.objects\
            .values_list("slug", flat=True))

        # find any running backends which currently
        # don't have objects, and fill in the gaps
        for name in settings.RAPIDSMS_BACKENDS.keys():

            if not name in known_backend_slugs:
                backend = PersistantBackend.objects.create(
                    slug=name)

                # log what we did to the console
                print "Added persistant backend %s" % backend
                known_backend_slugs.append(name)
