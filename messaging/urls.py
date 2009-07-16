#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import messaging.views as views

urlpatterns = patterns('',
    url(r"^messaging$",        views.index,  name="messaging-index"),
    url(r"^messaging/search$", views.search, name="messaging-search"),
    url(r"^messaging/all$",    views.all),
    url(r"^messaging/none$",   views.none),
    url(r"^messaging/clear$",  views.clear)
)
