import celery
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@celery.task
def receive_async(text, connection_id, message_id, fields):
    """Task used to send inbound message through router phases."""
    from rapidsms.models import Connection
    from rapidsms.router import get_router
    logger.debug('receive_async: %s' % text)
    router = get_router()
    # reconstruct incoming message
    connection = Connection.objects.select_related().get(pk=connection_id)
    message = router.new_incoming_message(text=text, connections=[connection],
                                          id_=message_id, fields=fields)
    try:
        # call process_incoming directly to skip receive_incoming
        router.process_incoming(message)
    except Exception:
        logger.exception("An error occurred processing the incoming message.")


@celery.task
def send_async(backend_name, id_, text, identities, context):
    """Task used to send outgoing messages to backends."""
    logger.debug('send_async: %s' % text)
    from rapidsms.router import get_router
    router = get_router()
    try:
        router.send_to_backend(backend_name=backend_name, id_=id_, text=text,
                               identities=identities, context=context)
    except Exception:
        logger.exception("The backend encountered an error while sending.")
