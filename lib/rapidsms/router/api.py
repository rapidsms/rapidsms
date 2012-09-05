import datetime

from rapidsms.models import Connection, Backend


def receive(text, backend_name=None, identity=None, connection=None,
            fields=None):
    """
    Takes an incoming message from a backend and passes it to a router for
    processing.  If a ``connection`` is passed, ``backend_name`` and
    ``identity`` are ignored.
    """
    if not connection:
        backend, _ = Backend.objects.get_or_create(name=backend_name)
        connection, _ = backend.connection_set.get_or_create(identity=identity)
    from rapidsms.router import get_router
    from rapidsms.messages import IncomingMessage
    message = IncomingMessage(connection, text, datetime.datetime.now(),
                              fields=fields)
    router = get_router()()
    router.start()
    router.incoming(message)
    router.stop()
    return message


def send(text, backend_name=None, identity=None, connection=None):
    """
    Takes an outgoing message passes it to a router for processing.  If a 
    ``connection`` is passed, ``backend_name`` and ``identity`` are ignored.
    """
    if not connection:
        backend, _ = Backend.objects.get_or_create(name=backend_name)
        connection, _ = backend.connection_set.get_or_create(identity=identity)
    from rapidsms.router import get_router
    from rapidsms.messages import OutgoingMessage
    message = OutgoingMessage(connection, text)
    router = get_router()()
    router.start()
    router.outgoing(message)
    router.stop()
    return message
