from django.db.models import Q

from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.db.tasks import receive, send_transmissions


class DatabaseRouter(BlockingRouter):

    def queue_message(self, direction, connections, text, fields=None):
        """Create Message and Transmission objects for messages."""
        from rapidsms.router.db.models import Message, Transmission
        dbm = Message.objects.create(text=text, direction=direction)
        transmissions = []
        for connection in connections:
            transmissions.append(Transmission(message=dbm, status='Q',
                                              connection=connection))
        Transmission.objects.bulk_create(transmissions)
        return dbm

    def new_incoming_message(self, connections, text, fields=None):
        """Queue message in DB for async inbound processing."""
        dbm = self.queue_message("I", connections, text, fields)
        receive.delay(message_id=dbm.pk)
        # don't return message to prevent futher processing
        # inbound processing will be handled within an async task
        return None

    def group_transmissions(self, transmissions, batch_size=200):
        """Divide transmissions by backend and into manageable chunks."""
        start = 0
        end = batch_size
        # divide transmissions by backend
        backends = transmissions.values_list('connection__backend_id',
                                             flat=True)
        for backend_id in backends.distinct():
            q = Q(connection__backend_id=backend_id)
            # filter down based on this backend and order by ID
            transmissions = transmissions.filter(q).order_by('id')
            while True:
                # divid transmissions into chunks of specified size
                batch = transmissions[start:end]
                if not batch.exists():
                    # query returned no rows, so we've seen all transmissions
                    break
                yield backend_id, batch
                start = end
                end += batch_size

    def backend_preparation(self, msg):
        """Queue message in DB rather than passing directly to backends."""
        # create queued message and associated transmissions
        dbm = self.queue_message("O", msg.connections, msg.text)
        # mark message as processing
        dbm.status = "P"
        dbm.save()
        for backend_id, trans in self.group_transmissions(dbm.transmissions):
            transmission_ids = trans.values_list('pk', flat=True)
            send_transmissions.delay(backend_id=backend_id,
                                     message_id=dbm.pk,
                                     transmission_ids=transmission_ids)
