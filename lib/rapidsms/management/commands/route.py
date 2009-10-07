#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.management.base import NoArgsCommand
from ...djangoproject import settings
from ...rapidsms import router


class Command(NoArgsCommand):
    help = "Starts the RapidSMS router."


    def handle_noargs(self, **options):

        # start logging to the screen and file
        # TODO: this shouldn't be here
        router.set_logger(
            settings.RAPIDSMS_CONF["log"]["level"],
            settings.RAPIDSMS_CONF["log"]["file"])

        # add each application from conf
        for name, conf in settings.RAPIDSMS_APPS.items():
            router.add_app(name, conf)

        # add each backend from conf
        for name, conf in settings.RAPIDSMS_BACKENDS.items():
            router.add_backend(conf.pop("type"), name, conf)

        # wait for incoming messages
        router.start()
