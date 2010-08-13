#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os
from django.conf.urls.defaults import *
from rapidsms.utils.modules import try_import
from ..conf import settings


# this list will be populated with the urls from the urls.urlpatterns of
# each installed app, then found by django as if we'd listed them here.
urlpatterns = []


for module_name in settings.INSTALLED_APPS:

    # leave django contrib apps alone. (many of them include urlpatterns
    # which shouldn't be auto-mapped.) this is a hack, but i like the
    # automatic per-app mapping enough to keep it. (for now.)
    if module_name.startswith("django."):
        continue

    # attempt to import this app's urls
    module = try_import("%s.urls" % (module_name))
    if not hasattr(module, "urlpatterns"): continue

    # add the explicitly defined urlpatterns
    urlpatterns += module.urlpatterns

    # if the MEDIA_URL does not contain a hostname (ie, it's just an
    # http path), and we are running in DEBUG mode, we will also serve
    # the media for this app via this development server. in production,
    # these files should be served directly
    if settings.DEBUG:
        if not settings.MEDIA_URL.startswith("http://"):

            media_prefix = settings.MEDIA_URL.strip("/")
            module_suffix = module_name.split(".")[-1]

            # does urls.py have a sibling "static" dir? (media is always
            # served from "static", regardless of what MEDIA_URL says)
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

# examine all of the urlpatterns to see if there is a pattern
# defined for the root url / dashboard
has_dash = False
for pat in urlpatterns:
    if pat.regex.pattern == '^$':
        has_dash = True

# if there is no dashboard url, add the default
if not has_dash:
    from ..views import dashboard
    urlpatterns += patterns('', url(r'^$', dashboard),)
