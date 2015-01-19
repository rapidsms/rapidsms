import logging

from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.celery.tasks import receive_async, send_async


logger = logging.getLogger(__name__)


class CeleryRouter(BlockingRouter):
    """Skeleton router only used to execute the Celery task."""

    def is_eager(self, backend_name):
        """Return whether this backend is eager, meaning it runs
        tasks synchronously rather than queueing them to celery.

        A backend configures its eagerness by setting the backend
        configuration value ``router.celery.eager`` to True or
        False. The default is False.
        """
        try:
            backend = self.backends[backend_name]
        except KeyError:
            return False
        return backend._config.get('router.celery.eager', False)

    def receive_incoming(self, msg):
        """Queue incoming message to be processed in the background."""
        eager = self.is_eager(msg.connection.backend.name)
        if eager:
            logger.debug('Executing in current process')
            receive_async(msg.text, msg.connections[0].pk, msg.id,
                          msg.fields)
        else:
            logger.debug('Executing asynchronously')
            receive_async.delay(msg.text, msg.connections[0].pk, msg.id,
                                msg.fields)

    def backend_preparation(self, msg):
        """Queue outbound message to be processed in the background."""
        context = msg.extra_backend_context()
        grouped_identities = self.group_outgoing_identities(msg)
        for backend_name, identities in grouped_identities.items():
            eager = self.is_eager(backend_name)
            if eager:
                logger.debug('Executing in current process')
                send_async(backend_name, msg.id, msg.text, identities,
                           context)
            else:
                logger.debug('Executing asynchronously')
                send_async.delay(backend_name, msg.id, msg.text, identities,
                                 context)
