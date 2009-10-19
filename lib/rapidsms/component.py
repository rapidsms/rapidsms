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


    def __str__(self):
        return self.title


    def __repr__(self):
        return "<%s.%s>" %\
            (type(self).__module__, type(self).__name__)


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
                    'the RapidSMS APIs change. Sorry.') % (self, missing_keyword))

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
    
    def log_last_exception(self, *args, **kwargs):
        """
        TODO: docs
        """
        return self.router.log_last_exception(
            *args, **kwargs)
