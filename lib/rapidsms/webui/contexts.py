#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.config import Config
import os

def apps(request):
    conf = Config(os.environ["RAPIDSMS_INI"])
    return { "apps": conf["rapidsms"]["apps"] }

