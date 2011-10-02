# this is here to get around circular imports for now.  methods here will
# move to rapidsms.router once that gets revamped
import datetime

from ..conf import settings
from ..router import get_router
from ..models import Connection, Backend
from ..utils.modules import try_import


def handle_incoming(text, backend_name=None, identity=None, connection=None):
    """
    Takes an incoming message from a backend and passes it to a router for
    processing.  If a ``connection`` is passed, ``backend_name`` and
    ``identity`` are ignored.
    """
    if not connection:
        backend, _ = Backend.objects.get_or_create(name=backend_name)
        connection, _ = backend.connection_set.get_or_create(identity=identity)
    from ..messages import IncomingMessage
    message = IncomingMessage(connection, text, datetime.datetime.now())
    router = get_router()()
    router.start()
    router.incoming(message)
    router.stop()


def handle_outgoing(text, backend_name=None, identity=None, connection=None):
    """
    Takes an outgoing message passes it to a router for processing.  If a 
    ``connection`` is passed, ``backend_name`` and ``identity`` are ignored.
    """
    if not connection:
        backend, _ = Backend.objects.get_or_create(name=backend_name)
        connection, _ = backend.connection_set.get_or_create(identity=identity)
    from ..messages import OutgoingMessage
    message = OutgoingMessage(connection, text)
    router = get_router()()
    router.start()
    router.outgoing(message)
    router.stop()
