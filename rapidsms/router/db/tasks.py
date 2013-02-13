import datetime

import celery
from celery.utils.log import get_task_logger
from rapidsms.router.blocking import BlockingRouter


__all__ = ('recieve',)


logger = get_task_logger(__name__)


@celery.task
def receive(message_id):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    from rapidsms.models import Connection
    from rapidsms.router.db.models import Message
    dbm = Message.objects.get(pk=message_id)
    router = BlockingRouter()
    ids = dbm.transmissions.values_list('connection_id', flat=True)
    connections = Connection.objects.filter(id__in=list(ids))
    # create new message for inbound processing
    message = router.new_incoming_message(connections=connections,
                                          text=dbm.text, fields=None)
    # pass db message along with message so apps can reference it
    message.db = dbm
    router.start()
    try:
        router.receive_incoming(message)
    except Exception, exc:
        logger.exception(exc)
        dbm.transmissions.update(status='E', updated=datetime.datetime.now())
        dbm.set_status()
    finally:
        router.stop()
    if dbm.status != 'E':
        # mark message as being received
        dbm.transmissions.update(status='R', updated=datetime.datetime.now())
        dbm.set_status()


@celery.task
def send_transmissions(backend_id, message_id, transmission_ids):
    """Send message to backend with provided transmissions. Retry if failed."""
    from rapidsms.models import Backend
    from rapidsms.router.db.models import Message, Transmission
    backend = Backend.objects.get(pk=backend_id)
    dbm = Message.objects.get(pk=message_id)
    transmissions = Transmission.objects.filter(id__in=transmission_ids)
    # set (possibly reset) status to processing
    transmissions.update(status='P')
    identities = transmissions.values_list('connection__identity', flat=True)
    router = BlockingRouter()
    router.start()
    try:
        router.send_to_backend(backend_name=backend.name, id_=dbm.pk,
                               text=dbm.text, identities=identities,
                               context={})
    except Exception, exc:
        # log error, update database statuses, and re-execute this task
        logger.exception(exc)
        Message.objects.filter(pk=message_id).update(status='E')
        transmissions.update(status='E', updated=datetime.datetime.now())
        raise send_transmissions.retry(exc=exc)
    finally:
        router.stop()
    # no error occured, so mark these transmissions as sent
    transmissions.update(status='S', sent=datetime.datetime.now())
    # we don't know if there are more transmissions pending, so
    # we always set the status at the end of each batch
    dbm.set_status()
