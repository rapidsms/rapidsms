#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import os, sys
from rapidsms.djangoproject import settings
from rapidsms.utils.modules import try_import, get_module_path
from django.conf.urls.defaults import patterns, url


# this list will be populated with the
# urls from the urls.urlpatterns of each
# running rapidsms app, then imported by
# django as if we'd declared them all here
urlpatterns = []


for module_name in settings.RAPIDSMS_APPS.keys():

    # attempt to import this app's urls
    module = try_import("%s.urls" % (module_name))
    if module is None: continue

    # add the explicitly defined urlpatterns
    urlpatterns += module.urlpatterns

    # does urls.py have a sibling "static" dir?
    module_path = os.path.dirname(module.__file__)
    static_dir = "%s/static" % module_path
    if os.path.exists(static_dir):

        # found a static dir, so automatically serve those files
        # via django. this is frowned upon in production, since
        # the server isn't tough (or fast), but there are so many
        # places that static files can come from, i'm not sure how
        # we would auto-configure that in apache. maybe we could
        # extend manager.py, to output an http conf mapping all
        # of this stuff for apache?
        urlpatterns += patterns("", url(
            "^static/%s/(?P<path>.*)$" % module_name,
            "django.views.static.serve",
            {"document_root": static_dir}
        ))
