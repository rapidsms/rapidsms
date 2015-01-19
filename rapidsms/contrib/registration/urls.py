#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls import url
from . import views


urlpatterns = (
    url(r'^$', views.registration, name="registration"),
    url(r'^contact/add/$', views.contact, name="registration_contact_add"),
    url(r'^contact/bulk_add/$', views.contact_bulk_add, name="registration_bulk_add"),
    url(r'^(?P<pk>\d+)/edit/$', views.contact, name="registration_contact_edit"),
)
