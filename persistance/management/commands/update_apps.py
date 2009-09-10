#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from apps.persistance.models import PersistantApp
from rapidsms.webui import settings


class Command(NoArgsCommand):
    help = "Creates instances of the PersistantApp model for all running apps."


    def handle_noargs(self, **options):

        # fetch all of the apps (identified
        # by their module, which is unique)
        # that we already have objects for
        known_app_modules = list(PersistantApp.objects\
            .values_list("module", flat=True))

        # find any running apps which currently
        # don't have objects, and fill in the gaps
        for conf in settings.RAPIDSMS_APPS.values():
            module = conf["module"]

            if not module in known_app_modules:
                app = PersistantApp.objects.create(
                    title=conf["title"],
                    module=module)

                # log what we did to the console
                print "Added persistant app %s" % app
                known_app_modules.append(module)
