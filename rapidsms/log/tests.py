#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from nose.tools import assert_equals, assert_raises, nottest
from ..log.mixin import LoggerMixin


class LoggableStub(object, LoggerMixin):
    pass


# Warnings are captured by the logging handler in Django 1.5+.
# Since this is being deprecated, I'm just going to disable this test. It'll
# be removed in the next release.
@nottest
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

    # There should be 8 messages: 7 from above, plus
    # one more for LoggerMixin's own deprecation warning
    assert_equals(len(handler.buffer), 7 + 1)
    assert_equals(handler.buffer[3].name, "loggablestub")
    assert_equals(handler.buffer[3].msg, "This is a WARNING")

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
