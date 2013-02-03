from django.test import TestCase

from rapidsms.models import Connection
from rapidsms.tests.harness import CustomRouterMixin, MockBackend, ExceptionApp
from rapidsms.router.db import DatabaseRouter
from rapidsms.router.db.models import Message

try:
    from django.test.utils import override_settings
except ImportError:
    from rapidsms.tests.harness import setting as override_settings


@override_settings(INSTALLED_APPS=['rapidsms.contrib.echo'])
class DatabaseRouterTest(CustomRouterMixin, TestCase):
    """Tests for the DatabaseRouter class"""

    router_class = 'rapidsms.router.db.DatabaseRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend}}

    def test_queue_status(self):
        """queue_message() should set the queued status."""
        router = DatabaseRouter()
        dbm = router.queue_message("I", [self.create_connection()], "foo")
        self.assertEqual("Q", dbm.status)
        transmission = dbm.transmissions.all()[0]
        self.assertEqual("Q", transmission.status)

    def test_queue_single_connection(self):
        """A single transmission should be created for 1 connection."""
        connections = [self.create_connection()]
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(1, dbm.transmissions.count())

    def test_queue_multi_connections(self):
        """Multiple transmissions should be created for > 1 connection."""
        connections = [self.create_connection(), self.create_connection()]
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(2, dbm.transmissions.count())

    def test_queue_queryset_connections(self):
        """queue_message() can accept a queryset of connections."""
        self.create_connection()
        self.create_connection()
        connections = Connection.objects.all()
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(2, dbm.transmissions.count())

    def test_receive(self):
        """receive() creates an inbound Message."""
        self.receive(text="foo", connection=self.create_connection())
        dbm = Message.objects.all()[0]
        self.assertEqual("foo", dbm.text)
        self.assertEqual("I", dbm.direction)
        self.assertEqual(1, dbm.transmissions.count())

    def test_receive_status(self):
        """Inbound messages should be marked with R if no errors occured."""
        self.receive(text="foo", connection=self.create_connection())
        dbm = Message.objects.all()[0]
        self.assertEqual("R", dbm.status)
        transmission = dbm.transmissions.all()[0]
        self.assertEqual("R", transmission.status)

    def test_receive_status_with_error(self):
        """Inbound messages should be marked with E if an error occured."""
        with override_settings(INSTALLED_APPS=[ExceptionApp]):
            self.receive(text="foo", connection=self.create_connection())
            dbm = Message.objects.all()[0]
            self.assertEqual("E", dbm.status)
            transmission = dbm.transmissions.all()[0]
            self.assertEqual("E", transmission.status)

    def test_send_queue(self):
        """send() should create a DB message that's processing."""
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection(data={'backend': backend})
        self.send(text="foo", connections=[connection])
        dbm = Message.objects.all()[0]
        self.assertEqual('P', dbm.status)
