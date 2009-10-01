#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from persistance.models import PersistantApp
from rapidsms.djangoproject import settings


class Command(NoArgsCommand):
    help = "Creates instances of the PersistantApp model for all running apps."


    def handle_noargs(self, **options):

        # fetch all of the apps (identified by
        # their module name, which is unique)
        # that we already have objects for
        known_module_names = list(PersistantApp.objects\
            .values_list("module", flat=True))

        # find any running apps which currently
        # don't have objects, and fill in the gaps
        for module_name in settings.RAPIDSMS_APPS.keys():
            if not module_name in known_module_names:
                app = PersistantApp.objects.create(
                    module=module_name)

                # log what we did to the console
                print "Added persistant app %s" % app
                known_module_names.append(module_name)
