#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls import url
from . import views


urlpatterns = (
    url(r"^$", views.generate_identity, name='httptester-index'),
    url(r"^(?P<identity>\d+)/$", views.message_tester, name='httptester')
)
