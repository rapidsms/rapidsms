#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import logging
import logging.handlers
import random          
import sys
import os

LOG_CHANNEL = "rapidsms"
LOG_SIZE    = 1024*1024*5 # 5 MB
LOG_BACKUPS = 20 # number of logs to keep around
LOG_FORMAT  = "%(asctime)s %(levelname)s [%(component)s]: %(message)s"
LOG_LEVEL   = "info"
LOG_FILE    = "/tmp/rapidsms.log"

class Logger (object):
    """A simple wrapper around the standard python logger."""
    def __init__(self, level=LOG_LEVEL, file=LOG_FILE,
                       format=LOG_FORMAT, channel=LOG_CHANNEL, stderr=True):
        # set up a specific logger with our desired output level
        self.log = logging.getLogger(channel)
        self.log.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(format)
        try:
            # make the log dir if doesn't exists
            log_dir = os.path.dirname(file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # add the log message handler and formatter to the log
            file_handler = logging.handlers.RotatingFileHandler(
                file, maxBytes=LOG_SIZE, backupCount=LOG_BACKUPS)
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)
        except Exception, e:
            print >>sys.stderr, "Error starting log file %s: %s" % (file,e)
            stderr = True
        if stderr:
            stderr_handler = logging.StreamHandler()
            stderr_handler.setFormatter(formatter)
            self.log.addHandler(stderr_handler)
        
    def write(self, sender, level, msg, *args):
        level = getattr(logging, level.upper())
        kwargs = {"extra":{"component":sender.title}}
        self.log.log(level, msg, *args, **kwargs)
