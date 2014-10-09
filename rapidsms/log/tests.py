#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase

from ..log.mixin import LoggerMixin


class LoggableStub(object, LoggerMixin):
    pass


class LoggerTest(TestCase):
    def test_logger_raises_on_invalid_name_type(self):
        class BrokenLoggableStub(object, LoggerMixin):
            def _logger_name(self):
                return 123

        broken_logger = BrokenLoggableStub()

        with self.assertRaises(TypeError):
            broken_logger.debug()
