import celery
from celery.utils.log import get_task_logger

from rapidsms.router.blocking import BlockingRouter


__all__ = ('recieve',)


logger = get_task_logger(__name__)


@celery.task
def receive(message_id):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    from rapidsms.router.db.models import Message
    db_message = Message.objects.get(pk=message_id)
    # mark message as being received
    db_message.status = "R"
    db_message.save()
    router = BlockingRouter()
    connections = db_message.transmissions.values_list('connection', flat=True)
    message = router.new_incoming_message(connections=connections,
                                          text=db_message.text, fields=None)
    router.start()
    try:
        router.receive_incoming(message)
    except Exception, e:
        logger.exception(e)
        db_message.status = "E"
        db_message.save()
    finally:
        router.stop()


# @celery.task
# def send():

#     MessageConnection.objects.

#     router = BlockingRouter()
#     try:
#         router.start()
#         router.send_to_backend(backend_name=backend_name, id_=id_, text=text,
#                                identities=identities, context=context)
#         router.stop()
#     except Exception, e:
#         logger.exception(e)
