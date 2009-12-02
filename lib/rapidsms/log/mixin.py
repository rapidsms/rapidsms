#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import logging


class LoggerMixin():
    """
    This mixin provides a quick way to log from classes within the RapidSMS
    framework. It's mostly pasted from logging.LoggingAdaptor (which isn't
    available in < Py2.6), with a couple of backwards-compatibility tweaks.

    TODO: This is a ridiculously long doctest. Make it a unittest.


    # set up an temporary python logger, which
    # buffers ALL messages to inspect later

    >>> import logging
    >>> from logging.handlers\
          import MemoryHandler

    >>> log = logging.getLogger()
    >>> log.setLevel(logging.DEBUG)
    >>> handler = MemoryHandler(999)
    >>> log.addHandler(handler)


    # create an instance of a noisy example class
    # (this would be your app, backend, or whatever)

    >>> class MyLoggingClass(object, LoggerMixin):
    ...     def do_something(self):
    ...        self.info("This is an INFO message")
    ...        self.debug("This is a DEBUG message")
    ...        self.warning("This is a WARNING message")
    ...        self.error("This is an ERROR message")
    ...        self.critical("This is a CRITICAL message")

    >>> x = MyLoggingClass()
    >>> x.do_something()


    # check that the buffer contains
    # exactly those those messages

    >>> len(handler.buffer)
    5

    >>> handler.buffer[0].levelname
    'INFO'

    >>> handler.buffer[0].msg
    'This is an INFO message'
    """


    def _logger_name(self):
        """
        Returns the name of the log which will receive messages emitted by this
        object. This defaults to the class name (sanitized), but should almost
        always be overloaded by subclasses to make the hierarchy clear.

        >>> class MyLoggingClass(object, LoggerMixin):
        ...    pass

        >>> MyLoggingClass()._logger_name()
        'myloggingclass'
        """
        return type(self).__name__.lower()


    @property
    def _logger(self):
        name = self._logger_name()

        # check the type of the output of _log_name, since logging.getLogger
        # doesn't bother, resulting in an obscure explosion for non-strings
        if not isinstance(name, basestring):
            raise TypeError(
                "%s._logger_name returned '%r' (%s). (wanted a string)" %\
                (type(self).__name__, name, type(name).__name__))

        return logging.getLogger(name)


    def log(self, *args, **kwargs):
        return self._logger.log(*args, **kwargs)


    def debug(self, *args, **kwargs):
        """Logs a 'msg % args' with severity DEBUG."""
        return self.log(logging.DEBUG, *args, **kwargs)


    def info(self, *args, **kwargs):
        """Logs a 'msg % args' with severity INFO."""
        return self.log(logging.INFO, *args, **kwargs)


    def warning(self, *args, **kwargs):
        """Logs a 'msg % args' with severity WARNING."""
        return self.log(logging.WARNING, *args, **kwargs)

    warn  = warning


    def error(self, *args, **kwargs):
        """Logs a 'msg % args' with severity ERROR."""
        return self.log(logging.ERROR, *args, **kwargs)


    def critical(self, *args, **kwargs):
        """Logs a 'msg % args' with severity CRITICAL."""
        return self.log(logging.CRITICAL, *args, **kwargs)

    fatal = critical


    def exception(self, *args, **kwargs):
        """
        Log a 'msg % args' with severity ERROR, with the backtrace from
        the last exception raised.
        """

        kwargs['exc_info'] = True
        return self.error(*args, **kwargs)

    # backwards-compatibility
    log_last_exception = exception
