import celery
from celery.utils.log import get_task_logger
from django.db.models import Q

from rapidsms.router.blocking import BlockingRouter


__all__ = ('recieve',)


logger = get_task_logger(__name__)


@celery.task
def receive(message_id):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    # TODO: update status of transmission
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
    finally:
        router.stop()
    if dbm.status != 'E':
        # mark message as being received
        dbm.status = "R"
        dbm.save()


@celery.task
def send(message_id):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    from rapidsms.router.db.models import Message
    dbm = Message.objects.get(pk=message_id)
    # mark message as processing
    dbm.status = "P"
    dbm.save()
    transmissions = dbm.transmissions
    # first divide transmissions by backend
    backends = transmissions.values_list('connection__backend_id', flat=True)
    for backend_id in backends.distinct():
        q = Q(connection__backend_id=backend_id)
        # TODO: chunk transmissions into more managable lenths
        chunk = transmissions.filter(q).values_list('pk', flat=True)
        send_transmissions.delay(backend_id=backend_id,
                                 message_id=message_id,
                                 transmission_ids=chunk)


@celery.task
def send_transmissions(backend_id, message_id, transmission_ids):
    from rapidsms.models import Backend
    from rapidsms.router.db.models import Message, Transmission
    backend = Backend.objects.get(pk=backend_id)
    dbm = Message.objects.get(pk=message_id)
    transmissions = Transmission.objects.filter(id__in=transmission_ids)
    identities = transmissions.values_list('connection__identity',
                                           flat=True)
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
