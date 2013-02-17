import collections

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from rapidsms.models import Backend
from rapidsms.utils.modules import import_class


def get_router():
    """Return router defined by RAPIDSMS_ROUTER setting."""
    router = getattr(settings, 'RAPIDSMS_ROUTER',
                     'rapidsms.router.blocking.BlockingRouter')
    if isinstance(router, basestring):
        try:
            router = import_class(router)()
        except ImportError, e:
            raise ImproperlyConfigured(e)
    return router


def receive(text, connection, **kwargs):
    """
    Creates an incoming message and passes it to the router for processing.
    """
    router = get_router()
    message = router.new_incoming_message(connections=[connection], text=text,
                                          **kwargs)
    router.receive_incoming(message)
    return message


def send(text, connections, **kwargs):
    """
    Creates an outgoing message and passes it to the router to be processed
    and sent via the respective backend.
    """
    if not isinstance(connections, collections.Iterable):
        connections = [connections]
    router = get_router()
    message = router.new_outgoing_message(text=text, connections=connections,
                                          **kwargs)
    router.send_outgoing(message)
    return message


def lookup_connections(backend, identities):
    """Return connections associated with backend and identities."""
    if isinstance(backend, basestring):
        backend, _ = Backend.objects.get_or_create(name=backend)
    connections = []
    for identity in identities:
        connection, _ = backend.connection_set.get_or_create(identity=identity)
        connections.append(connection)
    return connections
