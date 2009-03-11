#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from config import Config
from router import Router

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
    if len(args) > 1:
        ini = args.pop(1)
    else:
        ini = "rapidsms.ini"
    conf = Config(ini)

    django_settings = None
    if "database" in conf:
        django_settings = load_django_environment(conf)

    print args
    if len(args) > 1 and django_settings:
        django_manage_wrapper(django_settings,args)
    else:
        # load up the message router
        router = Router(conf)
        router.info("RapidSMS Server started up")

        # wait for incoming messages
        router.start()
