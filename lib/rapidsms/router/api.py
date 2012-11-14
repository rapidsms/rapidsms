import datetime
import collections

from rapidsms.models import Backend


def receive(text, connection, fields=None):
    """
    Takes an incoming message from a backend and passes it to a router for
    processing.  If a ``connection`` is passed, ``backend_name`` and
    ``identity`` are ignored.
    """
    from rapidsms.router import get_router
    from rapidsms.messages import IncomingMessage
    router = get_router()()
    router.start()
    message = IncomingMessage(connection, text, datetime.datetime.now(),
                              fields=fields)
    router.receive_incoming(message)
    router.stop()
    return message


def send(text, connections):
    """
    Takes an outgoing message passes it to a router for processing.  If a
    ``connection`` is passed, ``backend_name`` and ``identity`` are ignored.
    """
    from rapidsms.router import get_router
    from rapidsms.messages import OutgoingMessage
    if not isinstance(connections, collections.Iterable):
        connections = [connections]
    router = get_router()()
    router.start()
    messages = []
    for connection in connections:
        message = OutgoingMessage(connection, text)
        router.send_outgoing(message)
        messages.append(message)
    router.stop()
    return messages


def lookup_connections(backend, identities):
    """Return connections associated with backend and identities"""
    if isinstance(backend, basestring):
        backend, _ = Backend.objects.get_or_create(name=backend)
    connections = []
    for identity in identities:
        connection, _ = backend.connection_set.get_or_create(identity=identity)
        connections.append(connection)
    return connections
