#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from nose.tools import assert_equals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.client import Client


def test_login():
    c = Client()
    login_url = reverse("rapidsms.views.login")

    # check that the login form is displayed.
    response = c.get(login_url)
    assert_equals(response.status_code, 200)

    # check that visitors can log in successfully.
    u = User.objects.create_user("testuser", "user@example.com", "testpass")
    response = c.post(login_url,
                      {'username': "testuser", 'password': "testpass"})
    assert_equals(response.status_code, 302)

    # clean up.
    u.delete()
