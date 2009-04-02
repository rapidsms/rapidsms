#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os


urlpatterns = []


# load the rapidsms configuration
from rapidsms.config import Config
conf = Config(os.environ["RAPIDSMS_INI"])


# iterate each of the active rapidsms apps (from the ini),
# and (attempt to) import the urls.py from each. it's okay
# if this fails, since not all apps have a webui

for rs_app in conf["rapidsms"]["apps"]:
    package_name = "apps.%s.urls" % (rs_app["type"])
    module = __import__(package_name, {}, {}, ["urlpatterns"])
    urlpatterns += module.urlpatterns

