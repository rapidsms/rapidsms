from django.test import TestCase

from rapidsms.tests.harness import CustomRouterMixin
from rapidsms.router.db.models import Message, Transmission


class DatabaseRouterTest(CustomRouterMixin, TestCase):
    """Tests for the DatabaseRouter class"""

    router_class = 'rapidsms.router.db.DatabaseRouter'
    disable_phases = True

    def test_receive_queue(self):
        """Received messages call BlockingRouter.receive_incoming."""
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
