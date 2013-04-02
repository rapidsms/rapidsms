from django.conf import settings

from rapidsms.tests.harness import CreateDataMixin
from rapidsms.tests.harness import backend
from rapidsms.router import lookup_connections, send, receive, get_router
from rapidsms.router import test as test_router
from rapidsms.backends.database.models import BackendMessage
from rapidsms.backends.database.outgoing import DatabaseBackend


__all__ = ('CustomRouter', 'MockBackendRouter')


class CustomRouterMixin(CreateDataMixin):
    """Inheritable TestCase-like object that allows Router customization."""

    router_class = 'rapidsms.router.blocking.BlockingRouter'
    backends = {}

    def _pre_rapidsms_setup(self):
        self._INSTALLED_BACKENDS = getattr(settings, 'INSTALLED_BACKENDS', {})
        self.set_backends()
        self._RAPIDSMS_ROUTER = getattr(settings, 'RAPIDSMS_ROUTER', None)
        self.set_router()

    def _post_rapidsms_teardown(self):
        setattr(settings, 'INSTALLED_BACKENDS', self._INSTALLED_BACKENDS)
        setattr(settings, 'RAPIDSMS_ROUTER', self._RAPIDSMS_ROUTER)

    def __call__(self, result=None):
        self._pre_rapidsms_setup()
        super(CustomRouterMixin, self).__call__(result)
        self._post_rapidsms_teardown()

    def receive(self, text, connection, **kwargs):
        """
        A wrapper around the ``receive`` API. See :ref:`receiving-messages`.
        """
        return receive(text, connection, **kwargs)

    def send(self, text, connections, **kwargs):
        """A wrapper around the ``send`` API. See :ref:`sending-messages`."""
        return send(text, connections, **kwargs)

    def get_router(self):
        """get_router() API wrapper."""
        return get_router()

    def set_backends(self):
        setattr(settings, 'INSTALLED_BACKENDS', self.backends)

    def set_router(self):
        setattr(settings, 'RAPIDSMS_ROUTER', self.router_class)

    def lookup_connections(self, backend, identities):
        """loopup_connections() API wrapper."""
        return lookup_connections(backend, identities)


class DatabaseBackendMixin(CustomRouterMixin):

    backends = {'mockbackend': {'ENGINE': DatabaseBackend}}

    def setUp(self):
        self.backend = self.create_backend(data={'name': 'mockbackend'})
        super(DatabaseBackendMixin, self).setUp()

    def lookup_connections(self, identities, backend='mockbackend'):
        """loopup_connections wrapper to use mockbackend by default"""
        return super(DatabaseBackendMixin, self).lookup_connections(backend,
                                                                    identities)

    @property
    def sent_messages(self):
        """Messages passed to backend."""
        return BackendMessage.objects.filter(name='mockbackend',
                                             direction='O')


class TestRouterMixin(CustomRouterMixin):
    """Test extension that uses TestRouter"""

    #: If `disable_phases` is True, messages will not be processed through the
    #: router phases.
    #: This is useful if you're not interested in testing application logic.
    #: For example, backends may use this flag to ensure messages are sent
    #: to the router, but don't want the message to be processed.
    disable_phases = False  # setting to True will disable router phases

    backends = {'mockbackend': {'ENGINE': backend.MockBackend}}

    def set_router(self):
        kwargs = {'disable_phases': self.disable_phases}
        if hasattr(self, 'apps'):
            kwargs['apps'] = self.apps
        if hasattr(self, 'backends'):
            kwargs['backends'] = self.backends
        self.router = test_router.TestRouter(**kwargs)
        # set RAPIDSMS_ROUTER to our newly created instance
        self.router_class = self.router
        super(TestRouterMixin, self).set_router()

    @property
    def inbound(self):
        """The list of message objects received by the router."""
        return self.router.inbound

    @property
    def outbound(self):
        """The list of message objects sent by the router."""
        return self.router.outbound

    @property
    def sent_messages(self):
        """The list of message objects sent to mockbackend."""
        return self.router.backends['mockbackend'].messages

    def clear_sent_messages(self):
        """Manually empty the outbox of mockbackend."""
        self.router.backends['mockbackend'].clear()

    def lookup_connections(self, identities, backend='mockbackend'):
        """A wrapper around the ``lookup_connections`` API.
        See :ref:`connection_lookup`."""
        return super(TestRouterMixin, self).lookup_connections(backend,
                                                               identities)
