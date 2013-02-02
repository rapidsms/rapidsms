from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.db.tasks import receive


class DatabaseRouter(BlockingRouter):

    def queue_message(self, direction, connections, text, fields):
        from rapidsms.router.db.models import Message
        message = Message.objects.create(text=text, direction=direction)
        for connection in connections:
            message.transmissions.create(connection=connection, status='Q')
        return message

    def new_incoming_message(self, connections, text, fields):
        message = self.queue_message("I", connections, text, fields)
        receive.delay(message_id=message.pk)
        # don't return message to prevent futher processing
        return None

    # def new_incoming_message(self, connections, text, fields):
    #     message = self.queue_message("O", connections, text, fields)
    #     return None
