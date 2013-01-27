import celery
from celery.utils.log import get_task_logger

from rapidsms.router.blocking import BlockingRouter


logger = get_task_logger(__name__)


@celery.task
def receive_async(msg):
    """Task used to send inbound message through router phases."""
    router = BlockingRouter()
    try:
        router.start()
        router.receive_incoming(msg)
        router.stop()
    except Exception, e:
        logger.exception(e)


@celery.task
def send_async(backend_name, id_, text, identities, context):
    """Task used to send outgoing messages to backends."""
    router = BlockingRouter()
    try:
        router.start()
        router.send_to_backend(backend_name=backend_name, id_=id_, text=text,
                               identities=identities, context=context)
        router.stop()
    except Exception, e:
        logger.exception(e)
