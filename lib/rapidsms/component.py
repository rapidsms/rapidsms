#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import Queue, sys, datetime, re
import config

Match_True  = re.compile(r'^(?:true|yes|1)$', re.I)
Match_False = re.compile(r'^(?:false|no|0)$', re.I)

def _logging_method (level):
    return lambda self, msg, *args: self.log(level, msg, *args)

class Component(object):
    @property
    def router (self):
        if hasattr(self, "_router"):
            return self._router

    def _get_name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return unicode(type(self).__name__)   

    def _set_name(self, name):
        self._name = name

    name = property(_get_name, _set_name)
   
    def configure (self):
        # overridden by App and Backend subclasses
        pass

    # helper method to get boolean config options
    def config_bool (self, value):
        if Match_True.match(value):
            return True
        elif Match_False.match(value):
            return False
        else:
            self.warn("config value '%s' isn't boolean!", value)
            return value

    # helper method to get boolean config options
    def config_list (self, value, separator=","):
        # if the value is iterable, make a list and return it.
        if hasattr(value, "__iter__"): return list(value)
        # else split on separator and filter blank values
        return config.to_list(value, separator)

    def log(self, level, msg, *args):
        if self.router:
            self.router.logger.write(self, level, msg, *args)

    debug    = _logging_method('debug')
    info     = _logging_method('info')
    warning  = _logging_method('warning')
    error    = _logging_method('error')
    critical = _logging_method('critical')

class Receiver(Component):
    def __init__(self):
        # do we want to put a limit on the queue size?
        # and what do we do if the queue gets full?
        self._queue = Queue.Queue()

    @property
    def message_waiting (self):
        return self._queue.qsize()
 
    def next_message (self, timeout=0.0):
        try:
            return self._queue.get(bool(timeout), timeout)
        except Queue.Empty:
            return None

    def send(self, message):
        # block until we can add to the queue.
        # it shouldn't be that long.
        self._queue.put(message, True)
