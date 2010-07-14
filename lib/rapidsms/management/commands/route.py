#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import logging, logging.handlers
from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from ...router import router
from ...conf import settings


class Command(NoArgsCommand):
    help = "Starts the %s router." % settings.PROJECT_NAME

    def handle_noargs(self, **options):

        numeric_level = getattr(logging, settings.LOG_LEVEL.upper())
        format = logging.Formatter(settings.LOG_FORMAT)

        router.logger = logging.getLogger()
        router.logger.setLevel(numeric_level)

        # start logging to the screen (via stderr)
        # TODO: allow the values used here to be
        # specified as arguments to this command
        handler = logging.StreamHandler()
        router.logger.addHandler(handler)
        handler.setLevel(numeric_level)
        handler.setFormatter(format)

        # start logging to file
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE, maxBytes=settings.LOG_SIZE,
            backupCount=settings.LOG_BACKUPS)
        router.logger.addHandler(file_handler)
        file_handler.setFormatter(format)

        # update the persistance models. (this is not djangonic at all.
        # it should be replaced with managers for App and Backend.)
        call_command("update_backends", verbosity=0)
        call_command("update_apps", verbosity=0)

        # add each application from conf
        for name in settings.INSTALLED_APPS:
            router.add_app(name)

        # add each backend
        for name, conf in settings.INSTALLED_BACKENDS.items():
            router.add_backend(name, conf.pop("ENGINE"), conf)

        # wait for incoming messages
        router.start()
