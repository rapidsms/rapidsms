import celery
from celery.utils.log import get_task_logger
from rapidsms.router.blocking import BlockingRouter


__all__ = ('recieve',)


logger = get_task_logger(__name__)


@celery.task
def receive(message_id):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    from rapidsms.router.db.models import Message
    dbm = Message.objects.get(pk=message_id)
    router = BlockingRouter()
    connections = dbm.transmissions.values_list('connection', flat=True)
    # create new message for inbound processing
    message = router.new_incoming_message(connections=connections,
                                          text=dbm.text, fields=None)
    # pass db message along with message so apps can reference it
    message.db = dbm
    router.start()
    try:
        router.receive_incoming(message)
    except Exception, e:
        logger.exception(e)
        dbm.status = "E"
        dbm.save()
        dbm.transmissions.update(status='E')
    finally:
        router.stop()
    if dbm.status != 'E':
        # mark message as being received
        dbm.status = "R"
        dbm.save()
        dbm.transmissions.update(status='R')


@celery.task
def send_transmissions(backend_id, message_id, transmission_ids):
    from rapidsms.models import Backend
    from rapidsms.router.db.models import Message, Transmission
    backend = Backend.objects.get(pk=backend_id)
    dbm = Message.objects.get(pk=message_id)
    transmissions = Transmission.objects.filter(id__in=transmission_ids)
    identities = transmissions.values_list('connection__identity', flat=True)
    router = BlockingRouter()
    router.start()
    # TODO: retry task if backend fails to send
    try:
        router.send_to_backend(backend_name=backend.name, id_=dbm.pk,
                               text=dbm.text, identities=identities,
                               context={})
    except Exception, e:
        logger.exception(e)
        dbm.status = "E"
        dbm.save()
    finally:
        router.stop()
