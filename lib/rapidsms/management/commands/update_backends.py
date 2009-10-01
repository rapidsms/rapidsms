#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from rapidsms.djangoproject import settings
from rapidsms.models import Backend


class Command(NoArgsCommand):
    help = "Creates an instance of the Backend model stub for each running backend."


    def handle_noargs(self, **options):

        # fetch all of the backends (identified by their
        # name) that we already have instances for
        known_backend_names = list(Backend.objects\
            .values_list("name", flat=True))

        # find any running backends which currently
        # don't have instances, and fill in the gaps
        for name in settings.RAPIDSMS_BACKENDS.keys():

            if not name in known_backend_names:
                backend = Backend.objects.create(
                    name=name)

                # log what we did to the console
                print "Added persistant backend %s" % backend
                known_backend_names.append(name)
