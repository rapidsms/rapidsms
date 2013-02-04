from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from rapidsms.tests import harness
from rapidsms.router import import_class, get_router, get_test_router
from rapidsms.router.base import BaseRouter
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.messages.outgoing import OutgoingMessage

try:
    from django.test.utils import override_settings
except ImportError:
    from rapidsms.tests.harness import setting as override_settings


class MockRouter(object):
    """Dummy class used to test importing with get_router()"""
    pass


class GetRouterTest(TestCase):
    """Tests for the get_router() API."""

    def test_import_class(self):
        """import_class() should raise excpected exceptions."""
        self.assertRaises(ImproperlyConfigured, import_class,
                          'rapidsms.tests.router.test_base.BadClassName')
        self.assertRaises(ImproperlyConfigured, import_class,
                          'rapidsms.tests.router.bad_module.MockRouter')
        self.assertEqual(
            import_class('rapidsms.tests.router.test_base.MockRouter'),
            MockRouter,
        )

    def test_get_router(self):
        """Test exceptions for bad input given to get_router()"""
        bad_module_router = 'rapidsms.tests.router.bad_module.MockRouter'
        bad_class_router = 'rapidsms.tests.router.test_base.BadClassName'
        good_mock_router = 'rapidsms.tests.router.test_base.MockRouter'
        with override_settings(RAPIDSMS_ROUTER=bad_module_router):
                self.assertRaises(ImproperlyConfigured, get_router)
        with override_settings(RAPIDSMS_ROUTER=bad_class_router):
                self.assertRaises(ImproperlyConfigured, get_router)
        with override_settings(RAPIDSMS_ROUTER=good_mock_router):
                self.assertTrue(isinstance(get_router(), MockRouter))

    def test_get_test_router(self):
        """Test exceptions for bad input given to get_test_router()"""
        bad_module_router = 'rapidsms.tests.router.bad_module.MockRouter'
        bad_class_router = 'rapidsms.tests.router.test_base.BadClassName'
        good_mock_router = 'rapidsms.tests.router.test_base.MockRouter'
        with override_settings(TEST_RAPIDSMS_ROUTER=bad_module_router):
            self.assertRaises(ImproperlyConfigured, get_test_router)
        with override_settings(TEST_RAPIDSMS_ROUTER=bad_class_router):
            self.assertRaises(ImproperlyConfigured, get_test_router)
        with override_settings(TEST_RAPIDSMS_ROUTER=good_mock_router):
            self.assertEqual(get_test_router(), MockRouter)


class BaseRouterTest(harness.CreateDataMixin, TestCase):

    def test_router_incoming_phases(self):
        """Incoming messages should trigger proper router phases."""
        router = BaseRouter()
        router.add_app(harness.MockApp)
        router.receive_incoming(self.create_incoming_message())
        self.assertEqual(set(router.apps[0].calls),
                         set(router.incoming_phases))

    def test_router_outgoing_phases(self):
        """Outgoing messages should trigger proper router phases."""
        router = BaseRouter()
        router.add_app(harness.MockApp)
        router.add_backend("mockbackend", harness.MockBackend)
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection(data={'backend': backend})
        msg = self.create_outgoing_message(data={'connections': [connection]})
        router.send_outgoing(msg)
        self.assertEqual(set(router.apps[0].calls),
                         set(router.outgoing_phases))

    def test_new_incoming_message(self):
        """BaseRouter should return a standard IncomingMessage by default."""
        router = BaseRouter()
        fields = {'foo': 'bar'}
        connection = self.create_connection()
        msg = router.new_incoming_message(text="foo", connections=[connection],
                                          fields=fields)
        self.assertTrue(isinstance(msg, IncomingMessage))
        self.assertEqual("foo", msg.text)
        self.assertEqual(connection, msg.connections[0])
        self.assertEqual(fields['foo'], msg.fields['foo'])

    def test_new_incoming_message_class(self):
        """Make sure you can customize the incoming message class."""
        class TestIncomingMessage(IncomingMessage):
            pass
        connection = self.create_connection()
        router = BaseRouter()
        msg = router.new_incoming_message(text="foo", connections=[connection],
                                          class_=TestIncomingMessage)
        self.assertTrue(isinstance(msg, TestIncomingMessage))

    def test_new_outgoing_message(self):
        """BaseRouter should return a standard OutgoingMessage by default."""
        router = BaseRouter()
        fields = {'foo': 'bar'}
        connection = self.create_connection()
        incoming_message = self.create_incoming_message()
        msg = router.new_outgoing_message(text="foo", connections=[connection],
                                          fields=fields,
                                          in_reply_to=incoming_message)
        self.assertTrue(isinstance(msg, OutgoingMessage))
        self.assertEqual("foo", msg.text)
        self.assertEqual(connection, msg.connections[0])
        self.assertEqual(fields['foo'], msg.fields['foo'])
        self.assertEqual(incoming_message, msg.in_reply_to)

    def test_new_outgoing_message_class(self):
        """Make sure you can customize the outgoing message class."""
        class TestOutgoingMessage(OutgoingMessage):
            pass
        connection = self.create_connection()
        router = BaseRouter()
        msg = router.new_outgoing_message(text="foo", connections=[connection],
                                          class_=TestOutgoingMessage)
        self.assertTrue(isinstance(msg, TestOutgoingMessage))
