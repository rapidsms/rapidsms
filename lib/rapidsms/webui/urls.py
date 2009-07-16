#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, sys
from rapidsms.webui import settings
from django.conf.urls.defaults import *


# this list will be populated with the
# urls from the urls.urlpatterns of each
# running rapidsms app, then imported by
# django as if we'd declared them all here
urlpatterns = []

# iterate each of the active rapidsms apps (from the ini),
# and (attempt to) import the urls.py from each. it's okay
# if this fails, since not all apps have a webui
for rs_app in settings.RAPIDSMS_APPS.values():
    try:
    
        # import the single "urlpatterns" attribute
        package_name = "%s.urls" % (rs_app["type"])
        module = __import__(package_name, {}, {}, ["urlpatterns"])

        # add the explicitly defined urlpatterns
        urlpatterns += module.urlpatterns

        # does urls.py have a sibling "static" dir?
        mod_dir = os.path.dirname(module.__file__)
        static_dir = "%s/static" % mod_dir
        if os.path.exists(static_dir):

            # found a static dir, so automatically serve those files
            # via django. this is frowned upon in production, since
            # the server isn't tough (or fast), but there are so many
            # places that static files can come from, i'm not sure how
            # we would auto-configure that in apache. maybe we could
            # extend manager.py, to output an http conf mapping all
            # of this stuff for apache?
            urlpatterns += patterns("", url(
                "^static/%s/(?P<path>.*)$" % rs_app["type"],
                "django.views.static.serve",
                {"document_root": static_dir }
            ))
    
    # urls.py couldn't be imported for this app...
    # was it because importing XXX.urls failed,
    # or because something INSIDE urls.py raised?
    except ImportError:
        
        # extract a backtrace, so we can find
        # out where the exception was raised
        tb = sys.exc_info()[2]
        
        # if there is a NEXT frame, it means that the __import__
        # statement in this file didn't fail -- the exception was
        # raised from within the imported urls.py. it's important
        # that we allow this error to propagate, to avoid silently
        # masking the error!
        if tb.tb_next:
            raise
