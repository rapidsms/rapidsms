from django.test import TestCase
from mock import Mock, patch
from rapidsms.tests.harness import CreateDataMixin

from rapidsms.tests.scripted import TestScript
from .views import registration


class TestRegister(TestScript):

    def testRegister(self):
        self.assertInteraction("""
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
        """)

    def testLang(self):
        self.assertInteraction("""
          8005551212 > lang english
          8005551212 < %s
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
          8005551212 > lang english
          8005551212 < I will speak to you in English.
          8005551212 > lang klingon
          8005551212 < Sorry, I don't speak "klingon".
        """ % ("You must JOIN or REGISTER yourself before you can set " +
               "your language preference."))

    def testHelp(self):
        self.assertInteraction("""
          8005551212 > lang
          8005551212 < To set your language, send LANGUAGE <CODE>
          8005551212 > register
          8005551212 < To register, send JOIN <NAME>
        """)


class TestViews(TestCase, CreateDataMixin):
    def setUp(self):
        # Make some contacts
        self.contacts = [self.create_contact() for i in range(2)]

    def test_registration(self):
        # The registration view calls render with a context that has a
        # contacts_table that has the contacts in its data
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(GET=Mock(get=Mock(return_value=1)))
            result = registration(request)
        context = render.call_args[0][2]
        table = context["contacts_table"]
        data = table.data.queryset
        self.assertEqual(len(self.contacts), len(list(table.data.queryset)))
