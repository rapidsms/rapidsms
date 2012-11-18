from django.conf import settings

from rapidsms.tests.harness import CreateDataMixin
from rapidsms.tests.harness import backend
from rapidsms.router import lookup_connections
from rapidsms.router import test as test_router


__all__ = ('CustomRouter', 'MockBackendRouter')


class CustomRouterMixin(CreateDataMixin):
    """
    Inheritable TestCase-like object that allows Router customization
    """
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


class MockBackendRouter(CustomRouterMixin):
    """
    Test exentions with BlockingRouter and MockBackend, and utility functions
    to examine outgoing messages
    """
    backends = {'mockbackend': {'ENGINE': backend.MockBackend}}

    def _post_rapidsms_teardown(self):
        super(MockBackendRouter, self)._post_rapidsms_teardown()
        self.clear()

    @property
    def outbox(self):
        return backend.outbox

    def clear(self):
        if hasattr(backend, 'outbox'):
            backend.outbox = []

    def lookup_connections(self, backend='mockbackend', identities=None):
        """loopup_connections wrapper to use mockbackend by default"""
        if not identities:
            identities = []
        return lookup_connections(backend, identities)


class TestRouterMixin(CustomRouterMixin):

    router_class = 'rapidsms.router.test.TestRouter'
    disable_phases = False  # setting to True will disable router phases

    def _pre_rapidsms_setup(self):
        super(TestRouterMixin, self)._pre_rapidsms_setup()
        self.reset_router()
        test_router.disable_phases = self.disable_phases

    def _post_rapidsms_teardown(self):
        super(TestRouterMixin, self)._post_rapidsms_teardown()
        self.reset_router()

    @property
    def inbound(self):
        return test_router.inbound

    @property
    def outbound(self):
        return test_router.outbound

    def reset_router(self):
        test_router.reset_router()
