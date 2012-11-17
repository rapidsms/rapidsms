from rapidsms.router.blocking import BlockingRouter
from rapidsms.router.celery.tasks import rapidsms_handle_message


class CeleryRouter(BlockingRouter):
    """Skeleton router only used to execute the Celery task."""

    def _logger_name(self):
        # override default logger name to be more explicit
        return __name__

    def _queue_message(self, msg, incoming):
        eager = False
        backend_name = msg.connection.backend.name
        try:
            backend = self.backends[backend_name]
        except KeyError:
            backend = None
        if backend:
            eager = backend._config.get('router.celery.eager', False)
        if eager:
            self.debug('Executing in current process')
            rapidsms_handle_message(msg, incoming)
        else:
            self.debug('Executing asynchronously')
            rapidsms_handle_message.delay(msg, incoming)

    def receive_incoming(self, msg):
        self._queue_message(msg, incoming=True)

    def send_outgoing(self, msg):
        self._queue_message(msg, incoming=False)
