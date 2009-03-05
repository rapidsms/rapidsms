#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import Queue, sys

class Component(object):
    @property
    def router (self):
        if hasattr(self._router):
            return self._router
    
    def log(self, level, msg):
        if self.router:
            self.router.log(level, msg)
        else:
            vars = (level.upper(), msg)
            print >>sys.stderr, "%s (could not be logged) %s\n" % vars

    def debug(self, msg):
        self.log('debug', msg)
    
    def info(self, msg):
        self.log('info', msg)
        
    def warning(self, msg):
        self.log('warning', msg)
    
    def error(self, msg):
        self.log('error', msg)
    
    def critical(self, msg):
        self.log('critical', msg)

class Receiver(object):
    # do we want to put a limit on the queue size?
    # and what do we do if the queue gets full?
    self._queue = Queue.Queue()

    @property
    def message_waiting (self):
        return self._queue.qsize()
 
    def next_message (self, timeout=0.0):
        try:
            return self._queue.get(timeout, timeout)
        except Queue.Empty:
            return None

    def send(self, message):
        # block until we can add to the queue.
        # it shouldn't be that long.
        self._queue.put(message, True)
