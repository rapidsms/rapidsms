#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from rapidsms.models import Backend
from ...conf import settings


class Command(NoArgsCommand):
    help = "Creates an instance of the Backend model stub for each " +\
        "running backend."

    def handle_noargs(self, **options):
        verbosity = int(options.get("verbosity", 1))

        # fetch all of the backends (identified by their
        # name) that we already have instances for
        known_backend_names = list(
            Backend.objects.values_list("name", flat=True)
        )

        # find any running backends which currently
        # don't have instances, and fill in the gaps
        for name in settings.INSTALLED_BACKENDS:
            if name not in known_backend_names:
                known_backend_names.append(name)
                backend = Backend.objects.create(
                    name=name)

                # log at the same level as syncdb's "created table..."
                # messages, to stay silent when called with -v 0
                if verbosity >= 1:
                    print "Added persistant backend %s" % backend
