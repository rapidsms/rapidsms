#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from .config import Config


def start (args):

    # if a specific conf has been provided (which it
    # will be, if we're inside the django reloader)
    if "RAPIDSMS_INI" in os.environ:
        ini = os.environ["RAPIDSMS_INI"]
    
    # use a local ini (for development)
    # if one exists, to avoid everyone
    # having their own rapidsms.ini
    elif os.path.isfile("local.ini"):
        ini = "local.ini"
    
    # otherwise, fall back
    else: ini = "rapidsms.ini"

    # add the ini path to the environment, so we can
    # access it globally, including any subprocesses
    os.environ["RAPIDSMS_INI"] = ini

    # read the config, which is shared
    # between the back and frontend
    conf = Config(ini)

    # if we found a config ini, try to configure Django
    if conf.sources:

        # import the webui settings, which builds the django
        # config from rapidsms.config, in a round-about way.
        # can't do it until env[RAPIDSMS_INI] is defined
        from rapidsms.djangoproject import settings

        # whatever we're doing, we'll need to call
        # django's setup_environ, to configure the ORM
        os.environ["DJANGO_SETTINGS_MODULE"] = "rapidsms.djangoproject.settings"
        from django.core.management import setup_environ, execute_manager
        setup_environ(settings)

    else:
        settings = None

    execute_manager(settings)
