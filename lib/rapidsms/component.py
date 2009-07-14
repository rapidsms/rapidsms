#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import Queue, sys, re, traceback
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
        
        # since no title was explicitly set, fall back to
        # name of the module that the class was declared in
        guess = str(self.__module__).split(".")
        if guess[-1] == 'app':
            return guess[-2]
        return guess[-1]
    
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
        
        # before passing the configuration data to the
        # component, store and remove the common stuff
        if "title" in kwargs: self._title = kwargs.pop("title")
        if "slug"  in kwargs: self._slug  = kwargs.pop("slug")
        
        # HACK: remove any internal stuff that was added by
        # config.py for the benefit of the webui (which doesn't
        # have access to the component itself, only the config object)
        kwargs.pop("module", None)
        kwargs.pop("path", None)
        
        try:
            self.configure(**kwargs)
        
        except TypeError, e:
            # "__init__() got an unexpected keyword argument '...'"
            if "unexpected keyword" in e.message:
                missing_keyword = e.message.split("'")[1]
                raise Exception("Component '%s' does not support a '%s' option."
                        % (self.title, missing_keyword))
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
