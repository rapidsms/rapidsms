#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from django.conf.urls.defaults import *
from rapidsms.utils.modules import try_import
from ..conf import settings

urlpatterns = []


for module_name in settings.INSTALLED_APPS:
    if not settings.MEDIA_URL.startswith("http://"):
        media_prefix = settings.MEDIA_URL.strip("/")
        module_suffix = module_name.split(".")[-1]

        # does the app have a child "static" dir? (media is always
        # served from "static", regardless of what MEDIA_URL says)
        module = try_import(module_name)
        if not module:
            continue
        module_path = os.path.dirname(module.__file__)
        static_dir = "%s/static" % (module_path)
        if os.path.exists(static_dir):

            # map to {{ MEDIA_URL }}/appname
            urlpatterns += patterns("", url(
                "^%s/%s/(?P<path>.*)$" % (
                    media_prefix,
                    module_suffix),
                "django.views.static.serve",
                {"document_root": static_dir}
            ))
