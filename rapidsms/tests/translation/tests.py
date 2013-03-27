from django.test.utils import override_settings
from rapidsms.models import Connection
from rapidsms.tests.harness import RapidTest
from rapidsms.tests.translation import app
from rapidsms.utils import translation as trans_helpers


class TranslationTestMixin(object):

    def setUp(self):
        super(TranslationTestMixin, self).setUp()
        self.backend = self.create_backend(data={'name': 'mockbackend'})

    def create_lang_connection(self, identity, language):
        """Create a connection with specified identity and language."""
        contact = self.create_contact(data={'language': language})
        connection = self.create_connection(data={'identity': identity,
                                                  'contact': contact,
                                                  'backend': self.backend})
        return connection


class TranslationRoutingTest(TranslationTestMixin, RapidTest):

    apps = [app.TranslationApp]

    def test_translation_override(self):
        """Message should be translated to the contact's preference."""
        en_conn = self.create_lang_connection('1000000000', 'en')
        es_conn = self.create_lang_connection('1000000001', 'es')
        # both contacts text in to RapidSMS
        self.receive('lang-hello', en_conn)  # English contact
        self.receive('lang-hello', es_conn)  # Spanish contact
        # response should be translated as expected
        self.assertEqual(len(self.outbound), 2)
        self.assertEqual(self.outbound[0].text, 'hello')
        self.assertEqual(self.outbound[1].text, 'hola')

    def test_broadcast(self):
        """Test example broadcast functionality."""
        self.create_lang_connection('1000000000', 'en')
        self.create_lang_connection('1000000001', 'en')
        self.create_lang_connection('1000000002', 'en')
        self.create_lang_connection('1000000003', 'es')
        self.create_lang_connection('1000000004', 'es')
        app.lang_broadcast()
        self.assertEqual(2, len(self.outbound))
        for message in self.outbound:
            if message.text == 'hello':
                self.assertEqual(3, len(message.connections))
            elif message.text == 'hola':
                self.assertEqual(2, len(message.connections))

    def test_contact_settings_langauge(self):
        """settings.LANGUAGE_CODE should not override Contact preference."""
        en_conn = self.create_lang_connection('1000000000', 'en')
        with override_settings(LANGUAGE_CODE='es'):
            self.receive('lang-hello', en_conn)
            self.assertEqual(self.outbound[0].text, 'hello')


class TranslationHelperTest(TranslationTestMixin, RapidTest):

    def test_connection_grouping(self):
        """Make sure group_connections returns list of (lang, connections)"""
        connections = (
            self.create_lang_connection('1000000000', 'en'),
            self.create_lang_connection('1000000001', 'en'),
            self.create_lang_connection('1000000002', 'en'),
            self.create_lang_connection('1000000003', 'es'),
            self.create_lang_connection('1000000004', 'es'),
            self.create_lang_connection('1000000005', 'fr'),
        )
        grouped_conns = list(trans_helpers.group_connections(connections))
        for lang, conns in grouped_conns:
            if lang == 'en':
                self.assertEqual(3, len(conns))
            elif lang == 'es':
                self.assertEqual(2, len(conns))
            elif lang == 'fr':
                self.assertEqual(1, len(conns))

    def test_connection_grouping_queryset(self):
        """Same test as above but with a QuerySet object."""
        self.create_lang_connection('1000000000', 'en')
        self.create_lang_connection('1000000001', 'en')
        self.create_lang_connection('1000000002', 'en')
        self.create_lang_connection('1000000003', 'es')
        self.create_lang_connection('1000000004', 'es')
        self.create_lang_connection('1000000005', 'fr')
        connections = Connection.objects.all()
        grouped_conns = list(trans_helpers.group_connections(connections))
        for lang, conns in grouped_conns:
            if lang == 'en':
                self.assertEqual(3, len(conns))
            elif lang == 'es':
                self.assertEqual(2, len(conns))
            elif lang == 'fr':
                self.assertEqual(1, len(conns))

    def test_connection_grouping_no_language(self):
        """group_connections should handle empty languages without issue."""
        connections = (
            self.create_lang_connection('1000000000', 'en'),
            self.create_lang_connection('1000000001', ''),
            self.create_lang_connection('1000000002', 'en'),
            self.create_lang_connection('1000000003', ''),
            self.create_lang_connection('1000000004', ''),
        )
        grouped_conns = list(trans_helpers.group_connections(connections))
        for lang, conns in grouped_conns:
            if lang == 'en':
                self.assertEqual(2, len(conns))
            elif lang == '':
                self.assertEqual(3, len(conns))
