#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import sys
import threading
import traceback
import time
import Queue

from django.dispatch import Signal

from .log.mixin import LoggerMixin
from .backends.base import BackendBase
from .apps.base import AppBase
from .conf import settings


class Router(object, LoggerMixin):
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

        self.accepting = False
        """TODO: Docs"""

        self._queue = Queue.Queue()
        """Pending incoming messages, populated by Router.incoming_message."""


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


    @staticmethod
    def _wait(func, timeout):
        """
        Keep calling *func* (a lambda function) until it returns True,
        for a maximum of *timeout* seconds. Return True if *func* does,
        or False if time runs out.
        """

        for n in range(0, timeout*10):
            if func(): return True
            else: time.sleep(0.1)

        return False


    def _start_backend(self, backend):
        """
        Start *backend*, and return True when it terminates. If an
        exception is raised, wait five seconds and restart it.
        """

        while True:
            try:
                self.debug("starting backend")
                started = backend.start()
                self.debug("backend %s terminated normally" % backend)
                return True
            
            except Exception, e:
                self.debug("caught exception in backend %s: %s" % (backend, e))
                backend.exception()

                # this flows sort of backwards. wait for five seconds
                # (to give the backend a break before retrying), but
                # abort and return if self.accepting is ever False (ie,
                # the router is shutting down). this ensures that we
                # don't delay shutdown, because that causes me to SIG
                # KILL, which prevents things from stopping cleanly.
                # also check _starting_backends to see if we're in the startup
                # state.  if we are, don't exit, because accepting won't be
                # True until we've finished starting up
                def should_exit():
                    return not (self._starting_backends or self.accepting)
                self.debug('waiting 15 seconds before retrying')
                if self._wait(should_exit, 15):
                    self.debug('returning from _start_backend')
                    return None


    def _start_all_backends(self):
        """
        Start all backends registed via Router.add_backend, by calling
        self._start_backend in a new daemon thread for each.
        """

        for backend in self.backends.values():
            worker = threading.Thread(
                name=backend._logger_name(),
                target=self._start_backend,
                args=(backend,))

            worker.daemon = True
            worker.start()

            # stash the worker thread in the backend, so we can check
            # whether it's still alive when _stop_all_backends is called
            backend.__thread = worker


    def _stop_all_backends(self):
        """
        Notify all backends registered via Router.add_backend that they
        should stop. This method cannot guarantee that backends **will**
        stop in a timely manner.
        """

        for backend in self.backends.values():
            alive = backend.__thread.is_alive
            if not alive(): continue
            backend.stop()

            if not self._wait(lambda: not alive(), 5):
                backend.error("Worker thread did not terminate")


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
        self._starting_backends = True
        self._start_all_backends()
        self._start_all_apps()
        self.running = True
        self.debug("Started")

        # now that all of the apps are started, we are ready to start
        # accepting messages. (if we tried to dispatch an message to an
        # app before it had started, it might not be configured yet.)
        self.accepting = True
        self._starting_backends = False

        try:
            while self.running:

                # fetch the next pending incoming message, if one is
                # available immediately. this increments the number of
                # "tasks" on the queue, which MUST be decremented later
                # to avoid deadlock during graceful shutdown. (it calls
                # _queue.join to ensure that all pending messages are
                # processed before stopping.).
                #
                # for more infomation on Queues, see:
                # help(Queue.Queue.task_done)
                try:
                    self.incoming(self._queue.get(block=False))
                    self._queue.task_done()

                # if there were no messages waiting, wait a very short
                # (in human terms) time before looping to check again.
                except Queue.Empty:
                    time.sleep(0.1)

        # stopped via ctrl+c
        except KeyboardInterrupt:
            self.warn("Caught KeyboardInterrupt")
            self.running = False

        # stopped via sys.exit
        except SystemExit:
            self.warn("Caught SystemExit")
            self.running = False

        # while shutting down, refuse to accept any new messages. the
        # backend(s) might have to discard them, but at least they can
        # pass the refusal back to the device/gateway where possible
        self.accepting = False

        self.debug("Stopping...")
        self._stop_all_backends()
        self._stop_all_apps()
        self.info("Stopped")


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

        if graceful:
            self.accepting = False
            self.join()

        self.running = False


    def join(self):
        """
        Block until the incoming message queue is empty. This method
        can potentially block forever, if it is called while this Router
        is accepting incoming messages.
        """

        self._queue.join()
        return True


    def incoming_message(self, msg):
        """
        Add *msg* to the incoming message queue and return True, or
        return False if this router is not currently accepting new
        messages (either because the queue is full, or we are busy
        shutting down).

        Adding a message to the queue is no guarantee that it will be
        processed any time soon (although the queue is regularly polled
        while Router.start is blocking), or responded to at all.
        """

        if not self.accepting:
            return False

        try:
            self._queue.put(msg)
            return True

        # if the queue is of a limited size, it may raise the Full
        # exception. there's no sense exploding (especially since we
        # have a bunch of pending messages), so just refuse to accept
        # it. hopefully, the backend can in turn refuse it
        except Queue.Full:
            return False


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

        # now send the message's responses
        msg.flush_responses()

        # we are no longer interested in this message... but some crazy
        # synchronous backends might be, so mark it as processed.
        msg.processed = True


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

        return msg.send_now()


# a single instance of the router singleton is available globally, like
# the db connection. it shouldn't be necessary to muck with this very
# often (since most interaction with the Router happens within an App or
# Backend, which have their own .router property), but when it is, it
# should be done via this process global
router = Router()
