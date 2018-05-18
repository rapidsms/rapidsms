#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase


class ViewTest(TestCase):
    def test_login(self):
        login_url = reverse("rapidsms-login")

        # check that the login form is displayed.
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        # check that visitors can log in successfully.
        User.objects.create_user("testuser", "user@example.com", "testpass")
        response = self.client.post(login_url,
                                    {'username': "testuser", 'password': "testpass"})
        self.assertEqual(response.status_code, 302)
