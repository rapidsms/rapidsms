#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import path
from .. import views

urlpatterns = (
    path('login/', views.RapidSMSLoginView.as_view(), name='rapidsms-login'),
    path('logout/', views.RapidSMSLogoutView.as_view(), name='rapidsms-logout'),
)
