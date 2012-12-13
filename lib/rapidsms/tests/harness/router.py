from django.conf import settings

from rapidsms.tests.harness import CreateDataMixin
from rapidsms.tests.harness import backend
from rapidsms.router import lookup_connections, send, receive
from rapidsms.router import test as test_router


__all__ = ('CustomRouter', 'MockBackendRouter')


class CustomRouterMixin(CreateDataMixin):
    """Inheritable TestCase-like object that allows Router customization."""

    router_class = 'rapidsms.router.blocking.BlockingRouter'
    backends = {}

    def _pre_rapidsms_setup(self):
        self._INSTALLED_BACKENDS = getattr(settings, 'INSTALLED_BACKENDS', {})
        setattr(settings, 'INSTALLED_BACKENDS', self.backends)
        self._RAPIDSMS_ROUTER = getattr(settings, 'RAPIDSMS_ROUTER', None)
        setattr(settings, 'RAPIDSMS_ROUTER', self.router_class)

    def _post_rapidsms_teardown(self):
        setattr(settings, 'INSTALLED_BACKENDS', self._INSTALLED_BACKENDS)
        setattr(settings, 'RAPIDSMS_ROUTER', self._RAPIDSMS_ROUTER)

    def __call__(self, result=None):
        self._pre_rapidsms_setup()
        super(CustomRouterMixin, self).__call__(result)
        self._post_rapidsms_teardown()

    def receive(self, text, connection, fields=None):
        """receive() API wrapper."""
        return receive(text, connection, fields)

    def send(self, text, connections):
        """send() API wrapper."""
        return send(text, connections)

    def lookup_connections(self, backend, identities):
        """loopup_connections() API wrapper."""
        return lookup_connections(backend, identities)


class TestRouterMixin(CustomRouterMixin):
    """Test extension that uses TestRouter"""

    disable_phases = False  # setting to True will disable router phases
    backends = {'mockbackend': {'ENGINE': backend.MockBackend}}

    def _pre_rapidsms_setup(self):
        self.set_router()
        super(TestRouterMixin, self)._pre_rapidsms_setup()

    def set_router(self):
        kwargs = {'disable_phases': self.disable_phases}
        if hasattr(self, 'apps'):
            kwargs['apps'] = self.apps
        if hasattr(self, 'backends'):
            kwargs['backends'] = self.backends
        self.router = test_router.TestRouter(**kwargs)
        # set RAPIDSMS_ROUTER to our newly created instance
        self.router_class = self.router

    @property
    def inbound(self):
        """Messages passed to Router.receive_incoming"""
        return self.router.inbound

    @property
    def outbound(self):
        """Messages passed to Router.send_outgoing"""
        return self.router.outbound

    @property
    def sent_messages(self):
        """Messages passed to MockBackend.send"""
        return self.router.backends['mockbackend'].messages

    def clear_sent_messages(self):
        """Clear messages sent to the mockbackend."""
        self.router.backends['mockbackend'].clear()

    def lookup_connections(self, identities, backend='mockbackend'):
        """loopup_connections wrapper to use mockbackend by default"""
        return super(TestRouterMixin, self).lookup_connections(backend,
                                                               identities)
