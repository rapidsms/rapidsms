from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.celery.tasks import receive_async, send_async


class CeleryRouter(BlockingRouter):
    """Skeleton router only used to execute the Celery task."""

    def _logger_name(self):
        # override default logger name to be more explicit
        return __name__

    def is_eager(self, backend_name):
        """Backends can manually specify whether or not celery is eager."""
        try:
            backend = self.backends[backend_name]
        except KeyError:
            return False
        return backend._config.get('router.celery.eager', False)

    def receive_incoming(self, msg):
        """Queue message to be processed in the background."""
        eager = self.is_eager(msg.connection.backend.name)
        if eager:
            self.debug('Executing in current process')
            receive_async(msg)
        else:
            self.debug('Executing asynchronously')
            receive_async.delay(msg)

    def send_to_backend(self, backend_name, id_, text, identities, context):
        """Pass processed message to backend(s)."""
        eager = self.is_eager(backend_name)
        if eager:
            self.debug('Executing in current process')
            send_async(backend_name=backend_name, id_=id_, text=text,
                       identities=identities, context=context)
        else:
            self.debug('Executing asynchronously')
            send_async.delay(backend_name=backend_name, id_=id_, text=text,
                             identities=identities, context=context)
