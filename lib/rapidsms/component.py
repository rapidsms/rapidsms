#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import Queue, sys, datetime, re, traceback
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
    
    @property
    def title(self):
        """Returns the verbose name of this component, which can contain any
           text, to clearly identify it to WebUI users and log viewers. This
           property may change at any time, so don't """
        if hasattr(self, "_title"):
            return self._title
        
        # since no title has explicitly set, fall back to
        # name of the file that the class was declared in
        return str(self.__module__).split(".")[-1]


    @property
    def slug(self):
        """Returns a sanitized version of the title, which can be
           assumed to be alphanumeric and unique. This is useful
           for embedding in URLs and Database keys."""
        
        if hasattr(self, "_slug"):
            return self._slug
        
        # no explict slug was set, so convert
        # the title into something URL-safe
        slug = self.title.lower().strip()
        slug = re.sub(r"[\s_\-]+", "-", slug)
        slug = re.sub(r"[^a-z\-]", "", slug)
        return slug


    def _configure(self, **kwargs):
        
        # store the entire configuration as an attr,
        # since most of the time, that's all we need
        self.config = kwargs

        try:
            self.configure(**kwargs)

        except TypeError, e:
            # if the configure method didn't handle all of the arguments,
            # the "... got an unexpected keyword argument '...'" exception
            # will be raised. components should accept any arguments (for
            # now), so re-raise with a very explicit exception
            if "unexpected keyword" in str(e):
                missing_keyword = str(e).split("'")[1]

                raise Exception((
                    'The "%s" component rejected the "%s" option. All components '  +\
                    'should accept arbitrary keyword arguments (via **kwargs) for ' +\
                    'the time being, to ensure that they continue to function as '  +\
                    'the RapidSMS APIs change. Sorry.') % (self.title, missing_keyword))

            # something else went wrong. allow it
            # to propagate, to avoid masking errors
            else:
                raise


    def configure (self, **kwargs):
        # overridden by App and Backend subclasses
        pass
    
    # helper method to require mandatory config options
    def config_requires (self, option, value):
        if value is None:
            raise Exception("'%s' component requires a '%s' configuration setting!" % (
                    self.name, option))
        return value

    # helper method to get boolean config options
    def config_bool (self, value):
        if Match_True.match(value):
            return True
        elif Match_False.match(value):
            return False
        else:
            self.warning("config value '%s' isn't boolean!", value)
            return value

    # helper method to get boolean config options
    def config_list (self, value, separator=","):
        # if the value is iterable, make a list and return it.
        if hasattr(value, "__iter__"): return list(value)
        # else split on separator and filter blank values
        return config.to_list(value, separator)

    def log(self, level, msg, *args):

        # find the router to log to (it may be attached
        # to this component, or it may BE this component)
        # and pass this message to it's designated logger
        router = self.router if self.router else self
        router.logger.write(self, level, msg, *args)

    debug    = _logging_method('debug')
    info     = _logging_method('info')
    warning  = _logging_method('warning')
    error    = _logging_method('error')
    critical = _logging_method('critical')
    
    def log_last_exception(self, msg=None, level="error"):
        """Logs an exception, to allow rescuing of unexpected
        errors without discarding the debug information or
        killing the entire process."""
        
        # fetch the traceback for this exception, as
        # it would usually be dumped to the STDERR
        str = traceback.format_exc()
        
        # prepend the error message, if one was provided
        # (sometimes the exception alone is enough, but
        # the called *should* provide more info)
        if msg is not None:
            str = "%s\n--\n%s" % (msg, str)
        
        # pass the message on it on to the logger
        self.log(level, str)


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
