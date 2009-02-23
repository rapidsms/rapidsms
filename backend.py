#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

if __name__ == "__main__":
    router = rapidsms.router.Router()
    conf = rapidsms.Config("config.json")

    # iterate the app names from the config,
    # and attempt to import each of them
    for app_name in conf["apps"]:
        try:
            app_mod_str = "apps.%s.app" % (app_name)
            app_mod = __import__(app_mod_str, {}, {}, [''])
            router.register_app(app_mod.App())

        # it's okay if an app couldn't be loaded
        # TODO: proper logging here (and everywhere!)
        except ImportError, err:
            print "Couldn't import app: %s" % (app_name)

    # wait for incoming sms
    router.serve_forever()
