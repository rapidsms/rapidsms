#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *

urlpatterns = []


# load the rapidsms configuration
from rapidsms.config import Config
conf = Config(os.environ["RAPIDSMS_INI"])


# iterate each of the active rapidsms apps (from the ini),
# and (attempt to) import the urls.py from each. it's okay
# if this fails, since not all apps have a webui
for rs_app in conf["rapidsms"]["apps"]:
    try:
        package_name = "apps.%s.urls" % (rs_app["type"])
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
    
    # urls.py couldn't be imported for
    # this app. no matter, just carry
    # on importing the others
    except ImportError:
        pass
    except AttributeError:
        # module was imported but didn't have url patters
        pass
