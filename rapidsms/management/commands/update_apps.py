#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import BaseCommand
from rapidsms.models import App
from rapidsms.apps.base import AppBase
from ...conf import settings


class Command(BaseCommand):
    help = "Creates instances of the App model stub for all running apps."

    def handle(self, **options):
        verbosity = int(options.get("verbosity", 1))

        # fetch all of the apps (identified by their module name,
        # which is unique) that we already have objects for
        known_module_names = list(App.objects.values_list("module", flat=True))

        # find any running apps which currently
        # don't have objects, and fill in the gaps
        for module_name in settings.INSTALLED_APPS:
            if module_name not in known_module_names:
                # Assure the module is a rapidsms app with an App class
                if AppBase.find(module_name):
                    known_module_names.append(module_name)
                    app = App.objects.create(
                        module=module_name)

                    # log at the same level as syncdb's "created table..."
                    # messages, to stay silent when called with -v 0
                    if verbosity >= 1:
                        self.stdout.write("Added persistent app %s" % app)
