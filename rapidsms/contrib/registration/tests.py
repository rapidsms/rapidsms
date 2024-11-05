from io import BytesIO
from unittest.mock import Mock, patch

from django.http import Http404, HttpRequest, HttpResponseRedirect, QueryDict
from django.test import TestCase
from django.urls import reverse

from rapidsms.contrib.registration import views
from rapidsms.models import Connection, Contact
from rapidsms.tests.harness import CreateDataMixin, LoginMixin
from rapidsms.tests.scripted import TestScript

RAPIDSMS_HANDLERS = [
    "rapidsms.contrib.registration.handlers.language.LanguageHandler",
    "rapidsms.contrib.registration.handlers.register.RegisterHandler",
]


class TestRegister(TestScript):
    handlers = RAPIDSMS_HANDLERS

    def testRegister(self):
        self.assertInteraction(
            """
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
        """
        )

    def testLang(self):
        self.assertInteraction(
            """
          8005551212 > lang english
          8005551212 < %s
          8005551212 > register as someuser
          8005551212 < Thank you for registering, as someuser!
          8005551212 > lang english
          8005551212 < I will speak to you in English.
          8005551212 > lang klingon
          8005551212 < Sorry, I don't speak "klingon".
        """
            % (
                "You must JOIN or REGISTER yourself before you can set "
                + "your language preference."
            )
        )

    def testHelp(self):
        self.assertInteraction(
            """
          8005551212 > lang
          8005551212 < To set your language, send LANGUAGE <CODE>
          8005551212 > register
          8005551212 < To register, send JOIN <NAME>
        """
        )


class TestViews(TestCase, CreateDataMixin, LoginMixin):
    def setUp(self):
        # Make some contacts
        self.contacts = [self.create_contact() for i in range(2)]
        self.backend = self.create_backend()
        # Give the first one some connections
        for i in range(2):
            self.create_connection(data={"contact": self.contacts[0]})

    def test_registration(self):
        # The registration view calls render with a context that has a
        # contacts_table that has the contacts in its data
        request = HttpRequest()
        request.GET = QueryDict("")
        self.login()
        request.user = self.user
        with patch("rapidsms.contrib.registration.views.render") as render:
            views.registration(request)
        context = render.call_args[0][2]
        table = context["contacts_table"]
        self.assertEqual(len(self.contacts), len(list(table.data)))

    def test_registration_render(self):
        # render actually works (django_tables2 and all)
        request = HttpRequest()
        request.GET = QueryDict("")
        self.login()
        request.user = self.user
        retval = views.registration(request)
        self.assertEqual(200, retval.status_code)

    def test_contact_existing_404(self):
        # Trying to edit a non-existing contact raises a 404
        with self.assertRaises(Http404):
            views.contact(Mock(), pk=27)

    def test_contact_existing(self):
        # GET on contact form with valid pk renders template with that contact
        contact = self.contacts[0]
        connection = contact.default_connection
        with patch("rapidsms.contrib.registration.views.render") as render:
            request = Mock(method="GET")
            self.login()
            request.user = self.user
            views.contact(request, pk=contact.pk)
        context = render.call_args[0][2]
        self.assertEqual(contact.pk, context["contact"].pk)
        form = context["contact_form"]
        data = form.initial
        self.assertEqual(contact.name, data["name"])
        self.assertEqual(contact.pk, form.instance.pk)
        formset = context["connection_formset"]
        forms = formset.forms
        instances = [f.instance for f in forms]
        # Connection should be in there
        self.assertIn(connection, instances)
        # Should be 1 more form than we have connections
        self.assertEqual(len(forms), 1 + len(contact.connection_set.all()))

    def test_contact_get(self):
        # GET on contact form with no pk allows creating new one
        with patch("rapidsms.contrib.registration.views.render") as render:
            request = Mock(method="GET")
            self.login()
            request.user = self.user
            views.contact(request)
        context = render.call_args[0][2]
        # ModelForms create a new unsaved instance
        self.assertIsNotNone(context["contact_form"].instance)
        self.assertTrue(context["contact_form"].instance.is_anonymous)
        self.assertEqual(1, len(context["connection_formset"].forms))

    def test_contact_update(self):
        # POST to contact view updates the contact and connections
        contact = self.contacts[0]
        data = {
            "name": "The Contact",
            "language": "wxyz",
            "submit": "Save Contact",
            "connection_set-0-id": "2",
            "connection_set-0-DELETE": "",
            "connection_set-0-backend": "1",
            "connection_set-0-contact": "1",
            "connection_set-0-identity": "4567",
            "connection_set-1-id": "",
            "connection_set-1-contact": "1",
            "connection_set-1-identity": "",
            "connection_set-1-backend": "",
            "connection_set-INITIAL_FORMS": "1",
            "connection_set-TOTAL_FORMS": "2",
            "connection_set-MAX_NUM_FORMS": "10",
        }
        with patch("rapidsms.contrib.registration.views.render"):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        new_contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(data["name"], new_contact.name)
        self.assertEqual(data["language"], new_contact.language)
        identities = [c.identity for c in contact.connection_set.all()]
        self.assertIn(data["connection_set-0-identity"], identities)

    def test_contact_update_add_connection(self):
        # POST to contact view can add a connection
        contact = self.contacts[0]
        data = {
            "name": "The Contact",
            "language": "wxyz",
            "submit": "Save Contact",
            "connection_set-0-id": "2",
            "connection_set-0-DELETE": "",
            "connection_set-0-backend": "1",
            "connection_set-0-contact": "1",
            "connection_set-0-identity": "4567",
            "connection_set-1-id": "",
            "connection_set-1-contact": "1",
            "connection_set-1-identity": "987654",
            "connection_set-1-backend": "1",
            "connection_set-INITIAL_FORMS": "1",
            "connection_set-TOTAL_FORMS": "2",
            "connection_set-MAX_NUM_FORMS": "10",
        }

        identities = [c.identity for c in contact.connection_set.all()]
        self.assertNotIn(data["connection_set-1-identity"], identities)

        with patch("rapidsms.contrib.registration.views.render") as render:
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        render.assert_not_called()
        new_contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(data["name"], new_contact.name)
        self.assertEqual(data["language"], new_contact.language)
        identities = [c.identity for c in contact.connection_set.all()]
        self.assertIn(data["connection_set-1-identity"], identities)

    def test_contact_delete(self):
        # Submitting with Delete button deletes the contact
        contact = self.contacts[0]
        data = {
            "name": "The Contact",
            "language": "wxyz",
            "delete_contact": "dontcare",
            "connection_set-0-id": "2",
            "connection_set-0-DELETE": "",
            "connection_set-0-backend": "1",
            "connection_set-0-contact": "1",
            "connection_set-0-identity": "4567",
            "connection_set-1-id": "",
            "connection_set-1-contact": "1",
            "connection_set-1-identity": "987654",
            "connection_set-1-backend": "1",
            "connection_set-INITIAL_FORMS": "1",
            "connection_set-TOTAL_FORMS": "2",
            "connection_set-MAX_NUM_FORMS": "10",
        }

        with patch("rapidsms.contrib.registration.views.render"):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        self.assertFalse(Contact.objects.filter(pk=contact.pk).exists())

    def test_contact_create(self):
        # POST with no existing contact creates a new one
        name = "A BRAND NEW CONTACT"
        data = {
            "name": name,
            "language": "wxyz",
            "submit": "Save Contact",
            "connection_set-0-id": "",
            "connection_set-0-DELETE": "",
            "connection_set-0-backend": "1",
            "connection_set-0-contact": "",
            "connection_set-0-identity": "4567",
            "connection_set-1-id": "",
            "connection_set-1-contact": "",
            "connection_set-1-identity": "",
            "connection_set-1-backend": "",
            "connection_set-INITIAL_FORMS": "0",
            "connection_set-TOTAL_FORMS": "2",
            "connection_set-MAX_NUM_FORMS": "10",
        }
        with patch("rapidsms.contrib.registration.views.render"):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        Contact.objects.get(name=name)

    def test_delete_connection(self):
        # POST can delete one of the connections
        contact = self.create_contact()
        # Give it two connections
        self.create_connection(data={"contact": contact})
        self.create_connection(data={"contact": contact})

        # Submit form filled out to delete a connection
        connections = contact.connection_set.all()
        data = {
            "name": "Joe User",
            "language": "en",
            "submit": "Save Contact",
            "connection_set-0-id": connections[0].pk,
            "connection_set-0-identity": connections[0].identity,
            "connection_set-0-backend": connections[0].backend.pk,
            "connection_set-0-contact": contact.pk,
            "connection_set-1-id": connections[1].pk,
            "connection_set-1-identity": connections[1].identity,
            "connection_set-1-backend": connections[1].backend.pk,
            "connection_set-1-contact": contact.pk,
            "connection_set-1-DELETE": "connection_set-1-DELETE",
            "connection_set-2-id": "",
            "connection_set-2-backend": "",
            "connection_set-2-identity": "",
            "connection_set-2-contact": "",
            "connection_set-TOTAL_FORMS": "3",
            "connection_set-MAX_NUM_FORMS": "10",
            "connection_set-INITIAL_FORMS": "2",
        }
        old_pk = connections[1].pk
        with patch("rapidsms.contrib.registration.views.render"):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        self.assertFalse(Connection.objects.filter(pk=old_pk).exists())

    def test_add_connection(self):
        # POST can add a new connection
        contact = self.create_contact()
        # Give it ONE connection
        self.create_connection(data={"contact": contact})

        # Submit form filled out to add another connection

        connections = contact.connection_set.all()
        data = {
            "name": "Joe User",
            "language": "en",
            "submit": "Save Contact",
            "connection_set-0-id": connections[0].pk,
            "connection_set-0-identity": connections[0].identity,
            "connection_set-0-backend": connections[0].backend.pk,
            "connection_set-0-contact": contact.pk,
            "connection_set-1-id": "",
            "connection_set-1-identity": "identity",
            "connection_set-1-backend": connections[0].backend.pk,
            "connection_set-1-contact": contact.pk,
            "connection_set-TOTAL_FORMS": "2",
            "connection_set-MAX_NUM_FORMS": "10",
            "connection_set-INITIAL_FORMS": "1",
        }
        with patch("rapidsms.contrib.registration.views.render"):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        self.assertEqual(2, Connection.objects.filter(contact=contact).count())
        conn = Connection.objects.get(identity="identity", contact=contact)
        self.assertEqual(connections[0].backend, conn.backend)


class TestBulkAdd(TestCase, CreateDataMixin, LoginMixin):
    def setUp(self):
        self.login()
        self.url = reverse("registration_bulk_add")

    def create_testfile(self, s):
        """Takes a str object and returns a file-like object that can be put in a POST request"""
        testfile = BytesIO(s.encode("utf-8"))
        testfile.name = "testfile"
        return testfile

    def test_bulk_get(self):
        # Just make sure the page loads
        rsp = self.client.get(self.url)
        self.assertEqual(200, rsp.status_code)

    def test_bulk_add(self):
        # We can upload a CSV file to create contacts & connections
        backend1 = self.create_backend()
        backend2 = self.create_backend()
        # Include a unicode name to make sure that works
        uname = "Name 1 ḀḂḈ ᵺ"
        data = [
            (uname, backend1.name, "11111"),
            ("Name 2", backend2.name, "22222"),
            ("Name 3", backend1.name, "33333"),
            ("Name 4", backend2.name, "44444"),
        ]
        # Create test file
        testfile_data = "\n".join([",".join(parts) for parts in data]) + "\n"
        testfile = self.create_testfile(testfile_data)
        rsp = self.client.post(self.url, data={"bulk": testfile})
        self.assertEqual(302, rsp.status_code)
        contacts = Contact.objects.all()
        self.assertEqual(4, contacts.count())
        names = [contact.name for contact in contacts]
        self.assertIn(uname, names)

    def test_bulk_add_no_lines(self):
        testfile = self.create_testfile("")
        rsp = self.client.post(self.url, data={"bulk": testfile})
        self.assertEqual(200, rsp.status_code)
        self.assertIn("csv_errors", rsp.context)
        self.assertEqual("No contacts found in file", rsp.context["csv_errors"])

    def test_bulk_add_bad_line(self):
        testfile = self.create_testfile("Field 1, field 2\n")
        rsp = self.client.post(self.url, data={"bulk": testfile})
        self.assertEqual(200, rsp.status_code)
        self.assertIn("csv_errors", rsp.context)
        self.assertEqual("Could not unpack line 1", rsp.context["csv_errors"])

    def test_bulk_add_bad_backend(self):
        testfile = self.create_testfile("Field 1, no_such_backend, 123\n")
        rsp = self.client.post(self.url, data={"bulk": testfile})
        self.assertEqual(200, rsp.status_code)
        self.assertIn("csv_errors", rsp.context)
        self.assertEqual("Could not find Backend.  Line: 1", rsp.context["csv_errors"])
