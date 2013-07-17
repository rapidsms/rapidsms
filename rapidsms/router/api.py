import collections

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from rapidsms.models import Backend, Connection
from rapidsms.utils.modules import import_class


def get_router():
    """Return router defined by RAPIDSMS_ROUTER setting."""
    router = getattr(settings, 'RAPIDSMS_ROUTER',
                     'rapidsms.router.blocking.BlockingRouter')
    if isinstance(router, basestring):
        try:
            router = import_class(router)()
        except ImportError as e:
            raise ImproperlyConfigured(e)
    return router


def receive(text, connection, **kwargs):
    """
    Creates an incoming message and passes it to the router for processing.

    :param text: text message
    :param connection: RapidSMS :py:class:`~rapidsms.models.Connection` object
    :param kwargs: Extra kwargs to pass to
        :py:class:`~rapidsms.messages.incoming.IncomingMessage` constructor
    :returns: :py:class:`~rapidsms.messages.incoming.IncomingMessage`
        object constructed by router. A returned
        message object does not indicate that router processing has
        finished or even started, as this depends on the router defined
        in :setting:`RAPIDSMS_ROUTER`.
    :rtype: :py:class:`~rapidsms.messages.incoming.IncomingMessage`
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

    Arbitrary arguments are passed along to
    :py:meth:`~rapidsms.router.blocking.BlockingRouter.new_outgoing_message`.

    :param text: text message
    :param connections: list or QuerySet of RapidSMS
        :py:class:`~rapidsms.models.Connection` objects
    :param kwargs: Extra kwargs to pass to
        :py:class:`~rapidsms.messages.outgoing.OutgoingMessage` constructor
    :returns: message constructed by router. A returned
              message object does not indicate that router processing has
              finished or even started, as this depends on the router defined
              in :setting:`RAPIDSMS_ROUTER`.
    :rtype: :py:class:`~rapidsms.messages.outgoing.OutgoingMessage`
    """
    if not isinstance(connections, collections.Iterable):
        connections = [connections]
    router = get_router()
    try:
        backend_name = getattr(settings, 'OUTGOING_BACKEND_NAME')
        # TODO -> test implication on large datasets
        connections = lookup_connections(backend_name, connections)
    except ValueError:
        pass
    message = router.new_outgoing_message(text=text, connections=connections,
                                          **kwargs)
    router.send_outgoing(message)
    return message


def lookup_connections(backend, identities):
    """
    Find connections associated with backend and identities. A new connection
    object will be created for every backend/identity pair not found.

    :param backend: backend name (as a string) or
        :py:class:`~rapidsms.backends.base.BackendBase` object
    :param identities: list of identities to find associated with the backend
    :returns: List of :py:class:`~rapidsms.models.Connection` objects
    """
    if isinstance(backend, basestring):
        backend, _ = Backend.objects.get_or_create(name=backend)
    connections = []
    for identity in identities:
        if isinstance(identity, Connection):
            _conn = identity
            connection, _ = backend.connection_set.get_or_create(identity=_conn.identity)
            connections.append(connection)
        else:
            # TODO -> investigate why identities is a "Connection" object, this can
            # confuse folks!! New connections are created with a __unicode__ representation of
            # a Connection object.
            connection, _ = backend.connection_set.get_or_create(identity=identity)
            connections.append(connection)
    return connections
