#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


# this module exists only to provide a place for the ROOT_URLCONF
# setting (in webui.settings) to point to, so django can use the
# {ROOT_URLCONF}.urlpatterns as a singular point of entry. the
# array (below) is populated in settings.py, by collating the
# urls.py of each running rapidsms app.


urlpatterns = []
