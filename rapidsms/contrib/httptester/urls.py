#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.urls import path
from . import views


urlpatterns = (
    path("", views.generate_identity, name='httptester-index'),
    path("<int:identity>/", views.message_tester, name='httptester')
)
