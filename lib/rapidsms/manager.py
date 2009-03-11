#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from config import Config
from router import Router
import os

def load_django_environment (conf):
    # import the webui (django) directory so that
    # we have the settings module for any apps
    # that may be using the database
    try:
        from django.core.management import setup_environ
        from webui import settings
       
        # configure the database from the [database] INI block    
        for key, val in conf["database"].items():
            option = "DATABASE_" + key.upper()
            setattr(settings, option, val)

        # add the RapidSMS apps to the Django INSTALLED_APPS
        for app in conf["rapidsms"]["apps"]:
            appname = str("apps.%s" % (app)) 
            settings.INSTALLED_APPS.append(appname)

        # add apps/ to TEMPLATE_DIRS
        #
        # FIXME: TBD

        setup_environ(settings)
        return settings

    # TODO: proper logging here and everywhere!
    except ImportError, err:
        log.error("Couldn't import webui, check your webui settings module")
        return None

def django_manage_wrapper (settings, argv):
    from django.core.management import execute_manager
    execute_manager(settings, argv) 

def start (args):
    # load the local config file
    if "RAPIDSMS_INI" in os.environ:
        ini = os.environ["RAPIDSMS_INI"]
    elif os.path.isfile("local.ini"):
        ini = "local.ini"
    else:
        ini = "rapidsms.ini"

    os.environ["RAPIDSMS_INI"] = ini

    conf = Config(ini)

    django_settings = None
    if "database" in conf:
        django_settings = load_django_environment(conf)

    if len(args) > 1 and django_settings:
        django_manage_wrapper(django_settings,args)
    else:
        # load up the message router
        level, file = conf["log"]["level"], conf["log"]["file"]
        router = Router()
        router.set_logger(level, file)
        router.info("RapidSMS Server started up")
 
        for app_conf in conf["rapidsms"]["apps"]:
            router.info("Adding app: %r" % app_conf)
            router.add_app(app_conf)

        for backend_conf in conf["rapidsms"]["backends"]:
            router.info("Adding backend: %r" % backend_conf)
            router.add_backend(backend_conf)

        # wait for incoming messages
        router.start()
