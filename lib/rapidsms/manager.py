#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from config import Config
from router import Router
import os

def start (args):
    
    # if a specific conf has been provided (which it
    # will be), if we're inside the django reloaded
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
    # spawned by django
    os.environ["RAPIDSMS_INI"] = ini

    # read the config, which is shared
    # between the back and frontend
    conf = Config(ini)


    # if one or more arguments were passed, we're
    # starting up django. this chunk of code was
    # copied almost verbatim from django's manage.py
    if len(args) > 1:
        os.environ["DJANGO_SETTINGS_MODULE"] = "rapidsms.webui.settings"
        from django.core.management import setup_environ, execute_manager
        from webui import settings
        
        setup_environ(settings)
        execute_manager(settings, args)
    
    
    # no arguments passed, so perform
    # the default action: START RAPIDSMS
    else:
        router = Router()
        router.set_logger(conf["log"]["level"], conf["log"]["file"])
        router.info("RapidSMS Server started up")
 
        # add each application from conf
        for app_conf in conf["rapidsms"]["apps"]:
            router.info("Adding app: %r" % app_conf)
            router.add_app(app_conf)

        # add each backend from conf
        for backend_conf in conf["rapidsms"]["backends"]:
            router.info("Adding backend: %r" % backend_conf)
            router.add_backend(backend_conf)

        # wait for incoming messages
        router.start()
