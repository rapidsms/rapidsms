#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

def load_django_environment (conf):
    # import the webui (django) directory so that
    # we have the settings module for any apps
    # that may be using the database
    try:
        import webui
        import django
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
        
    # TODO: proper logging here and everywhere!
    except ImportError, err:
        log.error("Couldn't import webui, check your webui settings module")

def django_manage_wrapper ():
    pass

def start_server (argv):
    # load the local config file
    if len(argv) > 1:
        ini = argv[1]
    else:
        ini = "rapidsms.ini"
    conf = rapidsms.Config(ini)

    if "database" in conf:
        load_django_environment(conf)
    
    # load up the message router
    router = rapidsms.router.Router(conf)
    router.info("RapidSMS Server started up")

    # wait for incoming messages
    router.start()
