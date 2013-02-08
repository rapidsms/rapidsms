import collections

from rapidsms.models import Backend


def receive(text, connection, **kwargs):
    """
    Creates an incoming message and passes it to the router for processing.
    """
    from rapidsms.router import get_router
    router = get_router()
    router.start()
    message = router.new_incoming_message(connections=[connection], text=text,
                                          **kwargs)
    if message:
        router.receive_incoming(message)
    router.stop()
    return message


def send(text, connections, **kwargs):
    """
    Creates an outgoing message and passes it to the router to be processed
    and sent via the respective backend.
    """
    from rapidsms.router import get_router
    if not isinstance(connections, collections.Iterable):
        connections = [connections]
    router = get_router()
    router.start()
    message = router.new_outgoing_message(text=text, connections=connections,
                                          **kwargs)
    if message:
        router.send_outgoing(message)
    router.stop()
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
