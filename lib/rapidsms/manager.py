#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from config import Config
from router import Router
import os, sys, shutil


# the Manager class is a bin for various RapidSMS specific management methods
class Manager (object):
    def _skeleton (self, tree):
        return os.path.join(os.path.dirname(__file__), "skeleton", tree)

    def startproject (self, conf, *args):
        name = args[0]
        shutil.copytree(self._skeleton("project"), name)

    def startapp (self, conf, *args):
        name = args[0]
        target = os.path.join("apps",name)
        shutil.copytree(self._skeleton("app"), target)
        print "Don't forget to add '%s' to your rapidsms.ini apps." % name


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

    # if one of the remaining hard-coded methods were invoked,
    # go do that. TODO: move those to rapidsms/management
    if len(args) > 1 and hasattr(Manager, args[1]):
        handler = getattr(Manager(), args[1])
        handler(*args[2:])

    # otherwise, let Django deal with it
    else:
        execute_manager(settings)
