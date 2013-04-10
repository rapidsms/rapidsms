import celery
from celery.utils.log import get_task_logger

from django.utils.timezone import now
from rapidsms.errors import MessageSendingError


__all__ = ('receive_async', 'send_transmissions')


logger = get_task_logger(__name__)


@celery.task
def receive_async(message_id, fields):
    """Retrieve message from DB and pass to BlockingRouter for processing."""
    from rapidsms.router.db.models import Message
    from rapidsms.router import get_router
    dbm = Message.objects.get(pk=message_id)
    router = get_router()
    message = router.create_message_from_dbm(dbm, fields)
    try:
        # call process_incoming directly to skip receive_incoming
        router.process_incoming(message)
    except Exception:
        logger.exception("Exception in router.process_incoming")
        dbm.transmissions.update(status='E', updated=now())
        dbm.set_status()
    if dbm.status != 'E':
        # mark message as being received
        dbm.transmissions.update(status='R', updated=now())
        dbm.set_status()


@celery.task
def send_transmissions(backend_id, message_id, transmission_ids):
    """Send message to backend with provided transmissions. Retry if failed."""
    from rapidsms.models import Backend
    from rapidsms.router.db.models import Message, Transmission
    from rapidsms.router import get_router
    backend = Backend.objects.get(pk=backend_id)
    dbm = Message.objects.select_related('in_response_to').get(pk=message_id)
    transmissions = Transmission.objects.filter(id__in=transmission_ids)
    # set (possibly reset) status to processing
    transmissions.update(status='P')
    identities = transmissions.values_list('connection__identity', flat=True)
    router = get_router()
    context = {}
    if dbm.in_response_to:
        context['external_id'] = dbm.in_response_to.external_id
    try:
        router.send_to_backend(backend_name=backend.name, id_=dbm.pk,
                               text=dbm.text, identities=list(identities),
                               context=context)
    except MessageSendingError as exc:
        # update database statuses, and re-execute this task
        logger.warning("Re-trying send_transmissions")
        Message.objects.filter(pk=message_id).update(status='E')
        transmissions.update(status='E', updated=now())
        raise send_transmissions.retry(exc=exc)
    # no error occured, so mark these transmissions as sent
    transmissions.update(status='S', sent=now())
    # we don't know if there are more transmissions pending, so
    # we always set the status at the end of each batch
    dbm.set_status()
