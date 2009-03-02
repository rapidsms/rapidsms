#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import logging
import logging.handlers


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}
LOG_SIZE    = 8192 # 8192 bytes = 64 kb
LOG_BACKUPS = 256 # number of logs to keep around
LOG_FORMAT  = "%(asctime)s %(levelname)s: %(message)s"


class Log():
    """A simple wrapper around the standard python logger."""

    def __init__(self, log_level="debug", log_file=None):
        try:
            # set up a specific logger with our desired output level
            import random          
            self.log = logging.getLogger(
                "backend.log.%d" % random.randint(0, 999999))
            self.log.setLevel(LOG_LEVELS[log_level])

            # add the log message handler and formatter to the log
            log_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=LOG_SIZE, backupCount=LOG_BACKUPS)
            log_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            self.log.addHandler(log_handler)
        except:
            # if we fail starting up the log file, just note it and continue
            print "Error starting log file, check your config and permissions"
            self.log = None
        
    def debug(self, msg):
        if self.log: self.log.debug(msg)
        print(msg)
    
    def info(self, msg):
        if self.log: self.log.info(msg)
        print(msg)
        
    def warning(self, msg):
        if self.log: self.log.warning(msg)
        print(msg)
    
    def error(self, msg):
        if self.log: self.log.error(msg)
        print(msg)
    
    def critical(self, msg):
        if self.log: self.log.critical(msg)
        print(msg)

