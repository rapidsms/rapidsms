#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import sys
import rapidsms

if __name__ == "__main__":
    # load the local config file
    if len(sys.argv) > 1:
        ini = sys.argv[1]
    else:
        ini = "rapidsms.ini"
    conf = rapidsms.Config(ini)
    
    # load up the message router
    router = rapidsms.router.Router()
    router.info("RapidSMS Server started up")

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
        log.error("Couldn't import webui, check your webui settings module")

    # iterate the app classes from the config,
    # and instantiate them
    for app_class in conf["rapidsms"]["apps"]:
        router.info("Adding app: %r" % app_class)
        router.add_app(app_class(router))

    # iterate the backend classes from the config,
    # and instantiate them
    for backend_class in conf["rapidsms"]["backends"]:
        router.info("Adding backend: %r" % backend_class)
        router.add_backend(backend_class(router))

    # wait for incoming sms
    router.start()
