#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views.decorators.http import require_GET


@login_required
@require_GET
def dashboard(request):
    return render(request, "dashboard.html")


class RapidSMSLoginView(LoginView):
    template_name = "rapidsms/login.html"


class RapidSMSLogoutView(LogoutView):
    template_name = "rapidsms/loggedout.html"
