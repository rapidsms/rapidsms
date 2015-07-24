from mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from rapidsms.contrib.echo.handlers.echo import EchoHandler
from rapidsms.errors import MessageSendingError
from rapidsms.models import Connection
from rapidsms.tests import harness
from rapidsms.tests.harness.backend import RaisesBackend, FailedIdentitiesBackend
from rapidsms.router.db import DatabaseRouter
from rapidsms.router.db.models import Message, Transmission
from rapidsms.router.db.tasks import send_transmissions, receive_async


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


class DatabaseRouterReceiveTest(harness.DatabaseBackendMixin, TestCase):
    """Tests for the DatabaseRouter class"""

    router_class = 'rapidsms.router.db.DatabaseRouter'

    def setUp(self):
        self.conn1 = self.lookup_connections(backend='mockbackend', identities=['5551212'])[0]
        self.conn2 = self.lookup_connections(backend='mockbackend', identities=['5552323'])[0]

    def test_queue_status(self):
        """queue_message() should set the queued status."""
        router = DatabaseRouter()
        dbm = router.queue_message("I", [self.conn1], "foo")
        self.assertEqual("Q", dbm.status)
        transmission = dbm.transmissions.all()[0]
        self.assertEqual("Q", transmission.status)

    def test_queue_single_connection(self):
        """A single transmission should be created for 1 connection."""
        connections = [self.conn1]
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(1, dbm.transmissions.count())

    def test_queue_multi_connections(self):
        """Multiple transmissions should be created for > 1 connection."""
        connections = [self.conn1, self.conn2]
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(2, dbm.transmissions.count())

    def test_queue_queryset_connections(self):
        """queue_message() can accept a queryset of connections."""
        # 2 connections were created in setUp
        connections = Connection.objects.all()
        router = DatabaseRouter()
        dbm = router.queue_message("I", connections, "foo")
        self.assertEqual(2, dbm.transmissions.count())

    def test_receive(self):
        """receive() creates an inbound Message."""
        self.receive(text="foo", connection=self.conn1)
        dbm = Message.objects.all()[0]
        self.assertEqual("foo", dbm.text)
        self.assertEqual("I", dbm.direction)
        self.assertEqual(1, dbm.transmissions.count())

    def test_receive_status(self):
        """Inbound messages should be marked with R if no errors occured."""
        self.receive(text="foo", connection=self.conn1)
        dbm = Message.objects.all()[0]
        self.assertEqual("R", dbm.status)
        transmission = dbm.transmissions.all()[0]
        self.assertEqual("R", transmission.status)

    @patch.object(EchoHandler, 'handle')
    def test_receive_status_with_error(self, mock_handle):
        """Inbound messages should be marked with E if an error occured."""
        mock_handle.side_effect = Exception
        self.receive(text="echo foo", connection=self.conn1)
        dbm = Message.objects.all()[0]
        self.assertEqual("E", dbm.status)
        transmission = dbm.transmissions.all()[0]
        self.assertEqual("E", transmission.status)

    def test_receive_message_id(self):
        """IncomingMessage.id should be set to the created database message."""
        msg = self.receive(text="foo", connection=self.conn1)
        dbm = Message.objects.all()[0]
        self.assertEqual(msg.id, dbm.pk)

    def test_receive_external_id(self):
        """Router should save external_id to database for future reference."""
        fields = {'external_id': 'ASDF1234'}
        msg = self.receive(text="foo", connection=self.conn1, fields=fields)
        dbm = Message.objects.all()[0]
        self.assertEqual("ASDF1234", msg.fields['external_id'])
        self.assertEqual("ASDF1234", dbm.external_id)

    def test_create_message_from_dbm(self):
        """Make sure the proper fields are passed through."""
        router = DatabaseRouter()
        dbm = router.queue_message(direction='I', text="foo",
                                   connections=[self.conn1])
        dbm2 = router.create_message_from_dbm(dbm, {'a': 'b'})
        self.assertEqual({'a': 'b'}, dbm2.fields)

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

    def test_receive_async_fields(self):
        """Make sure the proper fields are passed to receive_async."""
        with patch.object(receive_async, 'delay') as mock_method:
            connections = self.lookup_connections(['1112223333'])
            msg = self.receive("test", connections[0], fields={'a': 'b'})
        mock_method.assert_called_once_with(message_id=msg.id,
                                            fields=msg.fields)


class DatabaseRouterSendTest(harness.DatabaseBackendMixin, TestCase):
    """DatabaseRouter send tests."""

    router_class = 'rapidsms.router.db.DatabaseRouter'

    def create_trans(self, s1='Q', s2='Q', backend=None):
        backend = backend or self.backend
        Connection.objects.bulk_create((
            Connection(identity='1111111111', backend=backend),
            Connection(identity='2222222222', backend=backend),
            Connection(identity='3333333333', backend=backend),
            Connection(identity='4444444444', backend=backend),
        ))
        dbm = Message.objects.create(text="test", direction="O")
        for connection in Connection.objects.order_by('id')[:2]:
            dbm.transmissions.create(connection=connection, status=s1)
        for connection in Connection.objects.order_by('id')[2:]:
            dbm.transmissions.create(connection=connection, status=s2)
        ids = dbm.transmissions.order_by('id').values_list('id', flat=True)
        trans1 = dbm.transmissions.filter(id__in=ids[:2])
        trans2 = dbm.transmissions.filter(id__in=ids[2:])
        return dbm, trans1, trans2

    def create_many_transmissions(self, num, backend=None):
        backend = backend or self.backend
        # Create a message that will be sent to many connections
        message = Message.objects.create(text="test", direction="O")
        for i in range(num):
            connection = Connection.objects.create(identity="%07d" % i,
                                                   backend=backend)
            message.transmissions.create(connection=connection, status="Q")

    def test_send_successful_status(self):
        """Transmissions should be marked with S if no errors occured."""
        # create 2 batches (queued, queued)
        dbm, t1, t2 = self.create_trans(s1='Q', s2='Q')
        send_transmissions(self.backend.pk, dbm.pk, t1.values_list('id', flat=True))
        status = t1.values_list('status', flat=True).distinct()[0]
        self.assertEqual('S', status)

    def test_send_successful_message_status(self):
        """Message object should be updated if all transmissions were sent."""
        # create 2 batches (sent, queued)
        dbm, t1, t2 = self.create_trans(s1='S', s2='Q')
        send_transmissions(self.backend.pk, dbm.pk, t2.values_list('id', flat=True))
        dbm = Message.objects.all()[0]
        self.assertEqual('S', dbm.status)

    def test_send_successful_message_status_previous_error(self):
        """Message should be marked E even if current batch sends."""
        # create 2 batches (error, queued)
        dbm, t1, t2 = self.create_trans(s1='E', s2='Q')
        send_transmissions(self.backend.pk, dbm.pk, t2.values_list('id', flat=True))
        dbm = Message.objects.all()[0]
        self.assertEqual('E', dbm.status)

    def test_group_transmissions(self):
        """Transmissions should be grouped by batch_size."""
        # create 2 batches (queued, queued)
        dbm, t1, t2 = self.create_trans(s1='Q', s2='Q')
        router = DatabaseRouter()
        trans = list(router.group_transmissions(Transmission.objects.all(),
                                                batch_size=2))
        _, batch1 = trans[0]
        _, batch2 = trans[1]
        self.assertEqual(list(batch1.values_list('id', flat=True)),
                         list(t1.values_list('id', flat=True)))
        self.assertEqual(list(batch2.values_list('id', flat=True)),
                         list(t2.values_list('id', flat=True)))

    def test_group_transmissions_different_backends(self):
        """Test grouping works across transmissions with different backends."""
        other_backend = self.create_backend(data={'name': 'other_backend'})
        self.create_many_transmissions(7)
        self.create_many_transmissions(6, backend=other_backend)
        router = DatabaseRouter()
        result = list(router.group_transmissions(Transmission.objects.all(),
                                                 batch_size=4))
        # 4 total batches
        self.assertEqual(4, len(result))
        # first two batches should be lenth 4 and 3 (=7)
        self.assertEqual(4, len(result[0][1]))
        self.assertEqual(3, len(result[1][1]))
        # second two batches should be lenth 4 and 2 (=6)
        self.assertEqual(4, len(result[2][1]))
        self.assertEqual(2, len(result[3][1]))

    def test_group_transmissions_default_batch_size(self):
        """Default max batch size is 200"""
        self.create_many_transmissions(201)
        router = DatabaseRouter()
        result = list(router.group_transmissions(Transmission.objects.all()))
        self.assertEqual(2, len(result))  # 2 batches
        self.assertEqual(200, len(result[0][1]))  # first batch has 200

    def test_group_transmissions_custom_default_batch_size(self):
        """Default max batch size can be configured in settings"""
        self.create_many_transmissions(3)
        router = DatabaseRouter()
        with self.settings(DB_ROUTER_DEFAULT_BATCH_SIZE=2):
            transmissions = Transmission.objects.all()
            result = list(router.group_transmissions(transmissions))
        self.assertEqual(2, len(result))  # 2 batches
        self.assertEqual(2, len(result[0][1]))  # first batch has 2

    def test_send_doesnt_send_already_sent_transmissions(self):
        """If a transmission has already been sent, don't resend it.
        (This may occur during a retry, when some of the messages were sent and some failed)."""
        # create 2 batches (sent, queued)
        dbm, t1, t2 = self.create_trans(s1='S', s2='Q')
        both_transmisssion_sets = list(t1.values_list('id', flat=True)) + list(t2.values_list('id', flat=True))
        send_transmissions(self.backend.pk, dbm.pk, both_transmisssion_sets)
        dbm = Message.objects.get()
        self.assertEqual('S', dbm.status)
        # only 2 messages should be sent, both from t2
        self.assertEqual(2, len(self.sent_messages))
        self.assertEqual(
            set([m.identity for m in self.sent_messages]),
            set([t.connection.identity for t in t2])
        )

    def test_all_transmissions_set_to_E_if_backend_sending_error(self):
        error_backend = RaisesBackend(self.get_router(), 'error_backend')
        self.backends['error_backend'] = {'ENGINE': RaisesBackend}
        dbm, t1, t2 = self.create_trans(s1='Q', s2='Q', backend=error_backend.model)
        both_transmisssion_sets = list(t1.values_list('id', flat=True)) + list(t2.values_list('id', flat=True))
        with override_settings(INSTALLED_BACKENDS=self.backends):
            with self.assertRaises(MessageSendingError):
                send_transmissions(error_backend.model.pk, dbm.pk, both_transmisssion_sets)
        errored = Transmission.objects.filter(status='E')
        # all of the transmissions should have a status of 'E' now
        self.assertEqual(4, errored.count())

    def test_only_failed_transmissions_set_to_E(self):
        # FailedIdentitiesBackend will fail any messages to an identity with a '1' in it.
        # create_trans creates 4 identities, only one of which has a '1' in it, so we expect
        # one failure.
        error_backend = FailedIdentitiesBackend(self.get_router(), 'error_backend')
        self.backends['error_backend'] = {'ENGINE': FailedIdentitiesBackend}
        dbm, t1, t2 = self.create_trans(s1='Q', s2='Q', backend=error_backend.model)
        both_transmisssion_sets = list(t1.values_list('id', flat=True)) + list(t2.values_list('id', flat=True))
        with override_settings(INSTALLED_BACKENDS=self.backends):
            with self.assertRaises(MessageSendingError):
                send_transmissions(error_backend.model.pk, dbm.pk, both_transmisssion_sets)
        errored = Transmission.objects.filter(status='E')
        # only 1 of the transmissions should have a status of 'E' now
        self.assertEqual(1, errored.count())
