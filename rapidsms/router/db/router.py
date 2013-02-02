from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.db.tasks import receive, send


class DatabaseRouter(BlockingRouter):

    def queue_message(self, direction, connections, text, fields=None):
        """Create Message and Transmission objects for messages."""
        from rapidsms.router.db.models import Message
        msg = Message.objects.create(text=text, direction=direction)
        # TODO: update to use bulk insert ORM api
        for connection in connections:
            msg.transmissions.create(connection=connection, status='Q')
        return msg

    def new_incoming_message(self, connections, text, fields=None):
        """Queue message in DB for async inbound processing."""
        dbm = self.queue_message("I", connections, text, fields)
        receive.delay(message_id=dbm.pk)
        # don't return message to prevent futher processing
        # inbound processing will be handled within an async task
        return None

    def backend_preparation(self, msg):
        """Queue message in DB rather than passing directly to backends."""
        dbm = self.queue_message("O", msg.connections, msg.text)
        send.delay(message_id=dbm.pk)
