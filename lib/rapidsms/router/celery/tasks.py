from celery import task

from rapidsms.router.blocking import BlockingRouter


@task()
def rapidsms_handle_message(msg, incoming=True):
    """Simple Celery task to process messages via BlockingRouter."""

    logger = rapidsms_handle_message.get_logger()
    if incoming:
        direction_name = 'incoming'
    else:
        direction_name = 'outgoing'
    logger.debug('New %s message: %s' % (direction_name, msg))
    router = BlockingRouter()
    try:
        router.start()
        if incoming:
            router.incoming(msg)
        else:
            router.outgoing(msg)
        router.stop()
    except Exception, e:
        logger.exception(e)
    logger.debug('Complete')
