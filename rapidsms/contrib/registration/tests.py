# coding=utf-8
from StringIO import StringIO
from django.http import Http404, HttpRequest, HttpResponseRedirect, QueryDict
from django.test import TestCase
from mock import Mock, patch
from rapidsms.models import Connection, Contact
from rapidsms.tests.harness import CreateDataMixin, LoginMixin

from rapidsms.tests.scripted import TestScript
import rapidsms.contrib.registration.views as views


RAPIDSMS_HANDLERS = [
    "rapidsms.contrib.registration.handlers.language.LanguageHandler",
    "rapidsms.contrib.registration.handlers.register.RegisterHandler",
]


class TestRegister(TestScript):
    handlers = RAPIDSMS_HANDLERS

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


class TestViews(TestCase, CreateDataMixin, LoginMixin):
    def setUp(self):
        # Make some contacts
        self.contacts = [self.create_contact() for i in range(2)]
        self.backend = self.create_backend()
        # Give the first one some connections
        for i in range(2):
            self.create_connection(data={'contact': self.contacts[0]})

    def test_registration(self):
        # The registration view calls render with a context that has a
        # contacts_table that has the contacts in its data
        request = HttpRequest()
        request.GET = QueryDict('')
        self.login()
        request.user = self.user
        with patch('rapidsms.contrib.registration.views.render') as render:
            views.registration(request)
        context = render.call_args[0][2]
        table = context["contacts_table"]
        self.assertEqual(len(self.contacts), len(list(table.data.queryset)))

    def test_registration_render(self):
        # render actually works (django_tables2 and all)
        request = HttpRequest()
        request.GET = QueryDict('')
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
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="GET")
            self.login()
            request.user = self.user
            views.contact(request, pk=contact.pk)
        context = render.call_args[0][2]
        self.assertEqual(contact.pk, context['contact'].pk)
        form = context['contact_form']
        data = form.initial
        self.assertEqual(contact.name, data['name'])
        self.assertEqual(contact.pk, form.instance.pk)
        formset = context['connection_formset']
        forms = formset.forms
        instances = [f.instance for f in forms]
        # Connection should be in there
        self.assertIn(connection, instances)
        # Should be 1 more form than we have connections
        self.assertEqual(len(forms), 1 + len(contact.connection_set.all()))

    def test_contact_get(self):
        # GET on contact form with no pk allows creating new one
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="GET")
            self.login()
            request.user = self.user
            views.contact(request)
        context = render.call_args[0][2]
        # ModelForms create a new unsaved instance
        self.assertIsNotNone(context['contact_form'].instance)
        self.assertTrue(context['contact_form'].instance.is_anonymous)
        self.assertEqual(1, len(context['connection_formset'].forms))

    def test_contact_update(self):
        # POST to contact view updates the contact and connections
        contact = self.contacts[0]
        data = {
            u'name': u'The Contact',
            u'language': u'wxyz',
            u'submit': u'Save Contact',
            u'connection_set-0-id': u'2',
            u'connection_set-0-DELETE': u'',
            u'connection_set-0-backend': u'1',
            u'connection_set-0-contact': u'1',
            u'connection_set-0-identity': u'4567',
            u'connection_set-1-id': u'',
            u'connection_set-1-contact': u'1',
            u'connection_set-1-identity': u'',
            u'connection_set-1-backend': u'',
            u'connection_set-INITIAL_FORMS': u'1',
            u'connection_set-TOTAL_FORMS': u'2',
            u'connection_set-MAX_NUM_FORMS': u'10',
        }
        with patch('rapidsms.contrib.registration.views.render'):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        new_contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(data['name'], new_contact.name)
        self.assertEqual(data['language'], new_contact.language)
        identities = [c.identity for c in contact.connection_set.all()]
        self.assertIn(data['connection_set-0-identity'], identities)

    def test_contact_update_add_connection(self):
        # POST to contact view can add a connection
        contact = self.contacts[0]
        data = {
            u'name': u'The Contact',
            u'language': u'wxyz',
            u'submit': u'Save Contact',
            u'connection_set-0-id': u'2',
            u'connection_set-0-DELETE': u'',
            u'connection_set-0-backend': u'1',
            u'connection_set-0-contact': u'1',
            u'connection_set-0-identity': u'4567',
            u'connection_set-1-id': u'',
            u'connection_set-1-contact': u'1',
            u'connection_set-1-identity': u'987654',
            u'connection_set-1-backend': u'1',
            u'connection_set-INITIAL_FORMS': u'1',
            u'connection_set-TOTAL_FORMS': u'2',
            u'connection_set-MAX_NUM_FORMS': u'10',
        }

        identities = [c.identity for c in contact.connection_set.all()]
        self.assertNotIn(data['connection_set-1-identity'], identities)

        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        render.assert_called()
        new_contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(data['name'], new_contact.name)
        self.assertEqual(data['language'], new_contact.language)
        identities = [c.identity for c in contact.connection_set.all()]
        self.assertIn(data['connection_set-1-identity'], identities)

    def test_contact_delete(self):
        # Submitting with Delete button deletes the contact
        contact = self.contacts[0]
        data = {
            u'name': u'The Contact',
            u'language': u'wxyz',
            u'delete_contact': u"dontcare",
            u'connection_set-0-id': u'2',
            u'connection_set-0-DELETE': u'',
            u'connection_set-0-backend': u'1',
            u'connection_set-0-contact': u'1',
            u'connection_set-0-identity': u'4567',
            u'connection_set-1-id': u'',
            u'connection_set-1-contact': u'1',
            u'connection_set-1-identity': u'987654',
            u'connection_set-1-backend': u'1',
            u'connection_set-INITIAL_FORMS': u'1',
            u'connection_set-TOTAL_FORMS': u'2',
            u'connection_set-MAX_NUM_FORMS': u'10',
        }

        with patch('rapidsms.contrib.registration.views.render'):
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
        name = u'A BRAND NEW CONTACT'
        data = {
            u'name': name,
            u'language': u'wxyz',
            u'submit': u'Save Contact',
            u'connection_set-0-id': u'',
            u'connection_set-0-DELETE': u'',
            u'connection_set-0-backend': u'1',
            u'connection_set-0-contact': u'',
            u'connection_set-0-identity': u'4567',
            u'connection_set-1-id': u'',
            u'connection_set-1-contact': u'',
            u'connection_set-1-identity': u'',
            u'connection_set-1-backend': u'',
            u'connection_set-INITIAL_FORMS': u'0',
            u'connection_set-TOTAL_FORMS': u'2',
            u'connection_set-MAX_NUM_FORMS': u'10',
        }
        with patch('rapidsms.contrib.registration.views.render'):
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
        self.create_connection(data={'contact': contact})
        self.create_connection(data={'contact': contact})

        # Submit form filled out to delete a connection
        connections = contact.connection_set.all()
        data = {
            u'name': u'Joe User',
            u'language': u'en',
            u'submit': u"Save Contact",

            u'connection_set-0-id': connections[0].pk,
            u'connection_set-0-identity': connections[0].identity,
            u'connection_set-0-backend': connections[0].backend.pk,
            u'connection_set-0-contact': contact.pk,

            u'connection_set-1-id': connections[1].pk,
            u'connection_set-1-identity': connections[1].identity,
            u'connection_set-1-backend': connections[1].backend.pk,
            u'connection_set-1-contact': contact.pk,
            u'connection_set-1-DELETE': u"connection_set-1-DELETE",

            u'connection_set-2-id': u'',
            u'connection_set-2-backend': u'',
            u'connection_set-2-identity': u'',
            u'connection_set-2-contact': u'',

            u'connection_set-TOTAL_FORMS': u'3',
            u'connection_set-MAX_NUM_FORMS': u'10',
            u'connection_set-INITIAL_FORMS': u'2',
        }
        old_pk = connections[1].pk
        with patch('rapidsms.contrib.registration.views.render'):
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
        self.create_connection(data={'contact': contact})

        # Submit form filled out to add another connection

        connections = contact.connection_set.all()
        data = {
            u'name': u'Joe User',
            u'language': u'en',
            u'submit': u"Save Contact",

            u'connection_set-0-id': connections[0].pk,
            u'connection_set-0-identity': connections[0].identity,
            u'connection_set-0-backend': connections[0].backend.pk,
            u'connection_set-0-contact': contact.pk,

            u'connection_set-1-id': u'',
            u'connection_set-1-identity': 'identity',
            u'connection_set-1-backend': connections[0].backend.pk,
            u'connection_set-1-contact': contact.pk,

            u'connection_set-TOTAL_FORMS': u'2',
            u'connection_set-MAX_NUM_FORMS': u'10',
            u'connection_set-INITIAL_FORMS': u'1',
        }
        with patch('rapidsms.contrib.registration.views.render'):
            request = Mock(method="POST", POST=data)
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact(request, pk=contact.pk)
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        self.assertEqual(2, Connection.objects.filter(contact=contact).count())
        conn = Connection.objects.get(identity='identity', contact=contact)
        self.assertEqual(connections[0].backend, conn.backend)


class TestBulkAdd(TestCase, CreateDataMixin, LoginMixin):
    def test_bulk_get(self):
        # Just make sure the page loads
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="GET")
            views.contact_bulk_add(request)
        render.assert_called()

    def test_bulk_add(self):
        # We can upload a CSV file to create contacts & connections
        backend1 = self.create_backend()
        backend2 = self.create_backend()
        # Include a unicode name to make sure that works
        uname = u'Name 1 ḀḂḈ ᵺ'
        data = [
            (uname, backend1.name, u'11111'),
            (u'Name 2', backend2.name, u'22222'),
            (u'Name 3', backend1.name, u'33333'),
            (u'Name 4', backend2.name, u'44444'),
        ]
        # Create test file
        testfile = u"\n".join([u",".join(parts) for parts in data]) + u"\n"
        testfile_data = testfile.encode('utf-8')
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="POST",
                           FILES={'bulk': StringIO(testfile_data)})
            request.__class__ = HttpRequest
            self.login()
            request.user = self.user
            retval = views.contact_bulk_add(request)
        if not isinstance(retval, HttpResponseRedirect):
            context = render.call_args[0][2]
            self.fail(context['bulk_form'].errors + context['csv_errors'])
        self.assertTrue(isinstance(retval, HttpResponseRedirect))
        self.assertEqual(302, retval.status_code)
        contacts = Contact.objects.all()
        self.assertEqual(4, contacts.count())
        names = [contact.name for contact in contacts]
        self.assertIn(uname, names)

    def test_bulk_add_no_lines(self):
        testfile = ""
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="POST", FILES={'bulk': StringIO(testfile)})
            self.login()
            request.user = self.user
            retval = views.contact_bulk_add(request)
        self.assertFalse(isinstance(retval, HttpResponseRedirect))
        context = render.call_args[0][2]
        self.assertIn('csv_errors', context)
        self.assertEqual('No contacts found in file', context['csv_errors'])

    def test_bulk_add_bad_line(self):
        testfile = "Field 1, field 2\n"
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="POST", FILES={'bulk': StringIO(testfile)})
            self.login()
            request.user = self.user
            retval = views.contact_bulk_add(request)
        self.assertFalse(isinstance(retval, HttpResponseRedirect))
        context = render.call_args[0][2]
        self.assertIn('csv_errors', context)
        self.assertEqual('Could not unpack line 1', context['csv_errors'])

    def test_bulk_add_bad_backend(self):
        testfile = "Field 1, no_such_backend, 123\n"
        with patch('rapidsms.contrib.registration.views.render') as render:
            request = Mock(method="POST", FILES={'bulk': StringIO(testfile)})
            self.login()
            request.user = self.user
            retval = views.contact_bulk_add(request)
        self.assertFalse(isinstance(retval, HttpResponseRedirect))
        context = render.call_args[0][2]
        self.assertIn('csv_errors', context)
        self.assertEqual("Could not find Backend.  Line: 1",
                         context['csv_errors'])
