#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls import url
from . import views


urlpatterns = (
    url(r'^$', views.message_log, name="message_log"),
)
