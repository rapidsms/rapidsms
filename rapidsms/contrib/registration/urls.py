#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path
from . import views


urlpatterns = (
    path('', views.registration, name="registration"),
    path('contact/add/', views.contact, name="registration_contact_add"),
    path('contact/bulk_add/', views.contact_bulk_add, name="registration_bulk_add"),
    path('<int:pk>/edit/', views.contact, name="registration_contact_edit"),
)
