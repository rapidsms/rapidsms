from mock import patch

from django.test import TestCase

from rapidsms.tests.harness import CustomRouterMixin
from rapidsms.tests.harness.backend import MockBackend

from rapidsms.router.blocking import BlockingRouter
from rapidsms.router import get_router
from rapidsms.router.celery.tasks import send_async, receive_async


class CeleryRouterTest(CustomRouterMixin, TestCase):
    """Tests for the CeleryRouter proxy class"""

    router_class = 'rapidsms.router.celery.CeleryRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend}}

    def test_incoming(self):
        """Received messages call BlockingRouter.receive_incoming."""
        msg = self.create_incoming_message()
        with patch.object(BlockingRouter, 'receive_incoming') as mock_method:
            receive_async(msg)
        mock_method.assert_called_once_with(msg)

    def test_outgoing(self):
        """Sent messages should call send() method of backend."""
        data = {'id_': 'foo', 'text': 'bar', 'identities': ['1112223333'],
                'context': {}}
        with patch.object(MockBackend, 'send') as mock_method:
            send_async(backend_name='mockbackend', **data)
        mock_method.assert_called_once_with(**data)


class NoEagerBackendTest(CustomRouterMixin, TestCase):

    router_class = 'rapidsms.router.celery.CeleryRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend}}

    def test_eager_invalid_backend(self):
        """is_eager should return False if backend doesn't exist."""
        router = get_router()
        self.assertFalse(router.is_eager('foo'))

    def test_eager_not_set(self):
        """is_eager should return False if not set for specified backend."""
        router = get_router()
        self.assertFalse(router.is_eager('mockbackend'))


class EagerBackendTest(CustomRouterMixin, TestCase):

    router_class = 'rapidsms.router.celery.CeleryRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend,
                                'router.celery.eager': True}}

    def test_outgoing(self):
        """is_eager should return True if router.celery.eager is set."""
        router = get_router()
        self.assertTrue(router.is_eager('mockbackend'))
