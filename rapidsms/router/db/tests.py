from django.test import TestCase

from rapidsms.tests.harness import CustomRouterMixin, MockBackend
from rapidsms.router.db.models import Message, Transmission

try:
    from django.test.utils import override_settings
except ImportError:
    from rapidsms.tests.harness import setting as override_settings


@override_settings(INSTALLED_APPS=['rapidsms.contrib.echo'])
class DatabaseRouterTest(CustomRouterMixin, TestCase):
    """Tests for the DatabaseRouter class"""

    router_class = 'rapidsms.router.db.DatabaseRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend}}

    def test_receive_queue(self):
        """receive() should create both a Message and Transmission object."""
        connection = self.create_connection()
        self.receive(text="foo", connection=connection)
        self.assertEqual(1, Message.objects.count())
        self.assertEqual(1, Transmission.objects.count())

    def test_marked_as_received(self):
        """receive() task should mark message as received."""
        connection = self.create_connection()
        self.receive(text="foo", connection=connection)
        message = Message.objects.all()[0]
        self.assertEqual("R", message.status)

    def test_send_queue(self):
        """send() should create a DB message that's processing."""
        backend = self.create_backend(data={'name': 'mockbackend'})
        connection = self.create_connection(data={'backend': backend})
        self.send(text="foo", connections=[connection])
        dbm = Message.objects.all()[0]
        self.assertEqual('P', dbm.status)
