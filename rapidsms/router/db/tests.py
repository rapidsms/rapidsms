from django.test import TestCase
from django.test.utils import override_settings

from rapidsms.models import Connection
from rapidsms.tests import harness
from rapidsms.router.db import DatabaseRouter
from rapidsms.router.db.models import Message, Transmission
from rapidsms.router.db.tasks import send_transmissions


class MessageStatusTest(harness.CustomRouterMixin, TestCase):

    router_class = 'rapidsms.router.db.DatabaseRouter'

    def test_inbound_message_status_error(self):
        """Message should be E if transmissions are E."""
        dbm = Message.objects.create(text="test", direction="I")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='E')
        self.assertEqual('E', dbm.set_status())

    def test_inbound_message_status_queued(self):
        """Message should be Q if transmissions are Q."""
        dbm = Message.objects.create(text="test", direction="I")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='Q')
        self.assertEqual('Q', dbm.set_status())

    def test_inbound_message_status_received(self):
        """Message should be R if transmissions are R."""
        dbm = Message.objects.create(text="test", direction="I")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='R')
        self.assertEqual('R', dbm.set_status())

    def test_outbound_message_status_error(self):
        """Any transmission marked E means the message should be E."""
        dbm = Message.objects.create(text="test", direction="O")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='E')
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='S')
        self.assertEqual('E', dbm.set_status())

    def test_outbound_message_status_processing(self):
        """If transmissions aren't all sent or delivered, status shold be P."""
        dbm = Message.objects.create(text="test", direction="O")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='Q')
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='S')
        self.assertEqual('P', dbm.set_status())

    def test_outbound_message_status_sent(self):
        """If not all messages are delivered, then status should be S."""
        dbm = Message.objects.create(text="test", direction="O")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='S')
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='D')
        self.assertEqual('S', dbm.set_status())

    def test_outbound_message_status_delivered(self):
        """If all messages are delivered, then status should be S."""
        dbm = Message.objects.create(text="test", direction="O")
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='D')
        dbm.transmissions.create(connection=self.create_connection(),
                                 status='D')
        self.assertEqual('D', dbm.set_status())


@override_settings(INSTALLED_APPS=['rapidsms.contrib.echo'])
class DatabaseRouterReceiveTest(harness.CustomRouterMixin, TestCase):
    """Tests for the DatabaseRouter class"""

    router_class = 'rapidsms.router.db.DatabaseRouter'
    backends = {'mockbackend': {'ENGINE': harness.MockBackend}}

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
        with override_settings(INSTALLED_APPS=[harness.ExceptionApp]):
            self.receive(text="foo", connection=self.create_connection())
            dbm = Message.objects.all()[0]
            self.assertEqual("E", dbm.status)
            transmission = dbm.transmissions.all()[0]
            self.assertEqual("E", transmission.status)

    def test_receive_message_id(self):
        """IncomingMessage.id should be set to the created database message."""
        msg = self.receive(text="foo", connection=self.create_connection())
        dbm = Message.objects.all()[0]
        self.assertEqual(msg.id, dbm.pk)

    def test_receive_external_id(self):
        """Router should save external_id to database for future reference."""
        fields = {'external_id': 'ASDF1234'}
        msg = self.receive(text="foo", connection=self.create_connection(),
                           fields=fields)
        dbm = Message.objects.all()[0]
        self.assertEqual("ASDF1234", msg.fields['external_id'])
        self.assertEqual("ASDF1234", dbm.external_id)


@override_settings(INSTALLED_APPS=[harness.EchoApp])
class DatabaseRouterSendTest(harness.DatabaseBackendMixin, TestCase):
    """DatabaseRouter send tests."""

    router_class = 'rapidsms.router.db.DatabaseRouter'

    def create_trans(self, s1='Q', s2='Q'):
        Connection.objects.bulk_create((
            Connection(identity='1111111111', backend=self.backend),
            Connection(identity='2222222222', backend=self.backend),
            Connection(identity='3333333333', backend=self.backend),
            Connection(identity='4444444444', backend=self.backend),
        ))
        dbm = Message.objects.create(text="test", direction="O")
        for connection in Connection.objects.order_by('id')[:2]:
            dbm.transmissions.create(connection=connection, status=s1)
        for connection in Connection.objects.order_by('id')[2:]:
            dbm.transmissions.create(connection=connection, status=s2)
        ids = dbm.transmissions.order_by('id').values_list('id', flat=True)
        trans1 = dbm.transmissions.filter(id__in=ids[:2])
        trans2 = dbm.transmissions.filter(id__in=ids[2:])
        return self.backend, dbm, trans1, trans2

    def test_send_successful_status(self):
        """Transmissions should be marked with S if no errors occured."""
        # create 2 batches (queued, queued)
        backend, dbm, t1, t2 = self.create_trans(s1='Q', s2='Q')
        send_transmissions(backend.pk, dbm.pk, t1.values_list('id', flat=True))
        status = t1.values_list('status', flat=True).distinct()[0]
        self.assertEqual('S', status)

    def test_send_successful_message_status(self):
        """Message object should be updated if all transmissions were sent."""
        # create 2 batches (sent, queued)
        backend, dbm, t1, t2 = self.create_trans(s1='S', s2='Q')
        send_transmissions(backend.pk, dbm.pk, t2.values_list('id', flat=True))
        dbm = Message.objects.all()[0]
        self.assertEqual('S', dbm.status)

    def test_send_successful_message_status_previous_error(self):
        """Message should be marked E even if current batch sends."""
        # create 2 batches (error, queued)
        backend, dbm, t1, t2 = self.create_trans(s1='E', s2='Q')
        send_transmissions(backend.pk, dbm.pk, t2.values_list('id', flat=True))
        dbm = Message.objects.all()[0]
        self.assertEqual('E', dbm.status)

    def test_group_transmissions(self):
        """Transmissions should be grouped by batch_size."""
        # create 2 batches (queued, queued)
        backend, dbm, t1, t2 = self.create_trans(s1='Q', s2='Q')
        router = DatabaseRouter()
        trans = list(router.group_transmissions(Transmission.objects.all(),
                                                batch_size=2))
        _, batch1 = trans[0]
        _, batch2 = trans[1]
        self.assertEqual(list(batch1.values_list('id', flat=True)),
                         list(t1.values_list('id', flat=True)))
        self.assertEqual(list(batch2.values_list('id', flat=True)),
                         list(t2.values_list('id', flat=True)))

    def test_in_response_to(self):
        """Make sure responses set the in_response_to DB fields."""
        connection = self.lookup_connections(['1112223333'])[0]
        self.receive(text="ping", connection=connection)
        message = Message.objects.get(direction='I')
        response = Message.objects.get(direction='O')
        self.assertEqual(message.pk, response.in_response_to.pk)

    def test_in_response_to_external_id(self):
        """DatabaseRouter should maintain external_id through responses."""
        connection = self.lookup_connections(['1112223333'])[0]
        msg = self.receive("test", connection,
                           fields={'external_id': 'ABCD1234'})
        backend_msg = self.sent_messages[0]
        self.assertEqual(msg.fields['external_id'], backend_msg.external_id)

    # not sure how to test this...
    # def test_send_error(self):
    #     """Message should be marked E even if current batch sends."""
    #     backends = {'mockbackend': {'ENGINE': RaisesBackend}}
    #     with patch.object(send_transmissions, 'retry') as mock_method:
    #         with override_settings(INSTALLED_BACKENDS=backends):
    #             backend, dbm, t1, t2 = self.create_trans(s1='S', s2='Q')
    #             send_transmissions(backend.pk, dbm.pk,
    #                                t2.values_list('id', flat=True))
    #             status = t2.values_list('status', flat=True).distinct()[0]
    #             self.assertEqual('E', status)
