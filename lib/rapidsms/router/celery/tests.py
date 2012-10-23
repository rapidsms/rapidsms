from mock import patch, Mock

from django.test import TestCase

from rapidsms.router.blocking import BlockingRouter
from rapidsms.tests.harness.base import MockBackendRouter
from rapidsms.tests.harness.backend import MockBackend

from rapidsms.router.celery import CeleryRouter
from rapidsms.router.celery.tasks import rapidsms_handle_message


class CeleryRouterTest(MockBackendRouter, TestCase):
    """Tests for the CeleryRouter proxy class"""

    router_class = 'rapidsms.router.celery.CeleryRouter'

    def test_incoming(self):
        """Received messages should call _queue_message with incoming=True"""

        with patch.object(CeleryRouter, '_queue_message') as mock_method:
            message = self.receive("test", identity='1112223333')
        mock_method.assert_called_once_with(message, incoming=True)

    def test_outgoing(self):
        """Sent messages should call _queue_message with incoming=False"""

        with patch.object(CeleryRouter, '_queue_message') as mock_method:
            message = self.send("test", identity='1112223333')
        mock_method.assert_called_once_with(message, incoming=False)


class EagerBackendTest(MockBackendRouter, TestCase):

    router_class = 'rapidsms.router.celery.CeleryRouter'
    backends = {'mockbackend': {'ENGINE': MockBackend,
                                'rapidsms.router.celery.eager': True}}

    def test_outgoing(self):
        """Eager backends should call rapidsms_handle_message directly"""

        with patch('rapidsms.router.celery.tasks.rapidsms_handle_message') as mock_method:
            self.receive("test", identity='1112223333')
        mock_method.assert_called_once()


class HandleMessageTaskTest(MockBackendRouter, TestCase):
    """Tests specific to the rapidsms_handle_message Celery task"""

    def test_incoming_method_call(self):
        """BlockingRouter.incoming should be called if incoming is True"""

        message = Mock()
        with patch.object(BlockingRouter, 'incoming') as mock_method:
            rapidsms_handle_message(message, incoming=True)
        mock_method.assert_called_once_with(message)

    def test_outgoing_method_call(self):
        """BlockingRouter.outgoing should be called if outgoing is True"""

        message = Mock()
        with patch.object(BlockingRouter, 'outgoing') as mock_method:
            rapidsms_handle_message(message, incoming=False)
        mock_method.assert_called_once_with(message)
