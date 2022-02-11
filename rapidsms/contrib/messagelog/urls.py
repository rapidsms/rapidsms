#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path
from . import views


urlpatterns = (
    path('', views.message_log, name="message_log"),
)
