from django.test import TestCase
from django.core.urlresolvers import reverse


class HttpTesterViewTest(TestCase):

    def test_new_identity_redirect(self):
        """httptester-new should redirect to the primary httptester view"""
        response = self.client.get(reverse("httptester-new"))
        self.assertEquals(response.status_code, 302)
