#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

if __name__ == "__main__":
    # load the local config file
    conf = rapidsms.Config("config.ini")
    
    # load up the message router
    log.info("RapidSMS Server starting up...")
    router = rapidsms.router.Router()

    # import the webui (django) directory so that
    # we have the settings module for any apps
    # that may be using the database
    # TODO: make a check for if we have a webui...
    try:
        import webui
        import django
        from django.core.management import setup_environ
        from webui import settings
        setup_environ(settings)
    # TODO: proper logging here and everywhere!
    except ImportError, err:
        print "Couldn't import webui, check your webui settings module"

    # iterate the app names from the config,
    # and attempt to import each of them
    #for app_name in conf["apps"]:
    #    app_module_str = "apps.%s.app" % (app_name)
    #    app_module = __import__(app_module_str, {}, {}, [''])
    #    router.add_app(app_module.App())
    for app_class in conf["apps"]:
        router.add_app(app_class(router))

    # iterate the backend names from the config,
    # and attempt to connect to each of them
    for backend_class in conf["backends"]:
        router.add_backend(backend_class(router))

    # wait for incoming sms
    router.start()
