#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import sys
import traceback
import time

from django.dispatch import Signal

from ..log.mixin import LoggerMixin
from ..backends.base import BackendBase
from ..apps.base import AppBase
from ..conf import settings


class BaseRouter(object, LoggerMixin):
    """
    """

    incoming_phases = ("filter", "parse", "handle", "default", "cleanup")
    outgoing_phases = ("outgoing",)

    pre_start  = Signal(providing_args=["router"])
    post_start = Signal(providing_args=["router"])
    pre_stop   = Signal(providing_args=["router"])
    post_stop  = Signal(providing_args=["router"])


    def __init__(self):

        self.apps = []
        self.backends = {}
        self.logger = None

        self.running = False
        """TODO: Docs"""

    def add_app(self, module_name):
        """
        Find the app named *module_name*, instantiate it, and add it to
        the list of apps to be notified of incoming messages. Return the
        app instance.
        """

        cls = AppBase.find(module_name)
        if cls is None: return None

        app = cls(self)
        self.apps.append(app)
        return app

    def get_app(self, module_name):
        """Get a handle to one of our apps by module name.""" 
        cls = AppBase.find(module_name)
        if cls is None: return None
        
        for app in self.apps:
            if type(app) == cls:
                return app
            
        raise KeyError("The %s app was not found in the router!" % module_name)

    def add_backend(self, name, module_name, config=None):
        """
        Find the backend named *module_name*, instantiate it, and add it
        to the dict of backends to be polled for incoming messages, once
        the router is started. Return the backend instance.
        """

        cls = BackendBase.find(module_name)
        if cls is None: return None

        config = self._clean_backend_config(config or {})
        backend = cls(self, name, **config)
        self.backends[name] = backend
        return backend

    @staticmethod
    def _clean_backend_config(config):
        """
        Return ``config`` (a dict) with the keys downcased. (This is
        intended to make the backend configuration case insensitive.)
        """

        return dict([
            (key.lower(), val)
            for key, val in config.iteritems()
        ])

    def _start_all_backends(self):
        """
        Start all backends registered in this router.
        """
        for backend in self.backends.values():
            backend.start()

    def _stop_all_backends(self):
        """
        Stop all backends registered in this router.
        """
        for backend in self.backends.values():
            backend.stop()

    def _start_all_apps(self):
        """
        Start all apps registered via Router.add_app.
        """

        for app in self.apps:
            try:
                app.start()

            except:
                app.exception()

    def _stop_all_apps(self):
        """
        Stop all apps registered via Router.add_app.
        """

        for app in self.apps:
            try:
                app.stop()

            except:
                app.exception()

    def start(self):
        """
        Start polling the backends registered via Router.add_backend for
        incoming messages, and keep doing so until a KeyboardInterrupt
        or SystemExit is raised, or Router.stop is called.
        """

        # dump some debug info for now
        #self.info("BACKENDS: %r" % (self.backends))
        #self.info("APPS: %r" % (self.apps))

        self.info("Starting %s..." % settings.PROJECT_NAME)
        self.pre_start.send(self)
        self._start_all_backends()
        self._start_all_apps()
        self.running = True
        self.debug("Started")

    def stop(self, graceful=False):
        """
        Stop the router, which unblocks the Router.start method as soon
        as possible. This may leave unprocessed messages in the incoming
        or outgoing queues.

        If the optional *graceful* argument is True, the router does its
        best to avoid discarding any messages, by refusing to accept new
        incoming messages and blocking (by calling Router.join) until
        all currently pending messages are processed.
        """

        self.running = False

        self.debug("Stopping...")
        self._stop_all_backends()
        self._stop_all_apps()
        self.info("Stopped")

    def incoming_message(self, msg):
        """
        Queue or send immediately the incoming message.  Defaults to sending
        the message immediately.
        """
        self.incoming(msg)

    def incoming(self, msg):
        """
        Incoming phases:

        Filter:
          The first phase, before any actual work is done. This is the
          only phase that can entirely abort further processing of the
          incoming message, which it does by returning True.

        Parse:
          Don't do INSERTs or UPDATEs in here!

        Handle:
          Respond to messages here.

        Default:
          Only called if no responses were sent during the Handle phase.

        Cleanup:
          An opportunity to clean up anything started during earlier phases.
        """

        self.info("Incoming (%s): %s" %\
            (msg.connection, msg.text))

        try:
            for phase in self.incoming_phases:
                self.debug("In %s phase" % phase)

                if phase == "default":
                    if msg.handled:
                        self.debug("Skipping phase")
                        break

                for app in self.apps:
                    self.debug("In %s app" % app)
                    handled = False

                    try:
                        func = getattr(app, phase)
                        handled = func(msg)

                    except Exception, err:
                        app.exception()

                    # during the _filter_ phase, an app can return True
                    # to abort ALL further processing of this message
                    if phase == "filter":
                        if handled is True:
                            self.warning("Message filtered")
                            raise(StopIteration)

                    # during the _handle_ phase, apps can return True
                    # to "short-circuit" this phase, preventing any
                    # further apps from receiving the message
                    elif phase == "handle":
                        if handled is True:
                            self.debug("Short-circuited")
                            # mark the message handled to avoid the 
                            # default phase firing unnecessarily
                            msg.handled = True
                            break
                    
                    elif phase == "default":
                        # allow default phase of apps to short circuit
                        # for prioritized contextual responses.   
                        if handled is True:
                            self.debug("Short-circuited default")
                            break
                        
        except StopIteration:
            pass

    def outgoing(self, msg):
        """
        """

        self.info("Outgoing (%s): %s" %\
            (msg.connection, msg.text))

        for phase in self.outgoing_phases:
            self.debug("Out %s phase" % phase)
            continue_sending = True

            # call outgoing phases in the opposite order of the incoming
            # phases, so the first app called with an  incoming message
            # is the last app called with an outgoing message
            for app in reversed(self.apps):
                self.debug("Out %s app" % app)

                try:
                    func = getattr(app, phase)
                    continue_sending = func(msg)

                except Exception, err:
                    app.exception()

                # during any outgoing phase, an app can return True to
                # abort ALL further processing of this message
                if continue_sending is False:
                    self.warning("Message cancelled")
                    return False
