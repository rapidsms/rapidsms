#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equals, assert_raises
from ..log.mixin import LoggerMixin


class LoggableStub(object, LoggerMixin):
    pass


def test_logger_mixin():
    obj = LoggableStub()

    from logging.handlers import MemoryHandler
    import logging

    log = logging.getLogger()
    handler = MemoryHandler(999)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    obj.debug("This is a DEBUG message")
    obj.info("This is an INFORMATIVE message")
    obj.warning("This is a WARNING")
    obj.error("This is an ERROR")
    obj.critical("This is a CRITICAL error")
    obj.exception("This is an exception")
    obj.exception()

    assert_equals(len(handler.buffer), 7)
    assert_equals(handler.buffer[2].name, "loggablestub")
    assert_equals(handler.buffer[2].msg, "This is a WARNING")

    log.removeHandler(handler)


def test_logger_raises_on_invalid_name_type():
    class BrokenLoggableStub(object, LoggerMixin):
        def _logger_name(self):
            return 123

    broken_logger = BrokenLoggableStub()

    assert_raises(
        TypeError,
        broken_logger.debug,
        "This shouldn't work")
