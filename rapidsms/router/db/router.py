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

    def backend_preparation(self, msg):
        """Queue message in DB rather than passing directly to backends."""
        # create queued message and associated transmissions
        dbm = self.queue_message("O", msg.connections, msg.text)
        # mark message as processing
        dbm.status = "P"
        dbm.save()
        transmissions = dbm.transmissions
        # divide transmissions by backend
        backends = transmissions.values_list('connection__backend_id',
                                             flat=True)
        for backend_id in backends.distinct():
            q = Q(connection__backend_id=backend_id)
            # TODO: chunk transmissions into more managable lenths
            chunk = transmissions.filter(q).values_list('pk', flat=True)
            send_transmissions.delay(backend_id=backend_id,
                                     message_id=dbm.pk,
                                     transmission_ids=chunk)
