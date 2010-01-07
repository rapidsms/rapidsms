#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


import os, sys, threading, traceback, time, datetime, Queue

from django.dispatch import Signal

from .utils.modules import try_import, get_class
from .backends.base import BackendBase
from .log.mixin import LoggerMixin
from .app import App as AppBase


class Router (object, LoggerMixin):
    """
    >>> "wat"
    'wat'
    """

    incoming_phases = ('filter', 'parse', 'handle', 'catch', 'cleanup')
    outgoing_phases = ('outgoing', 'pre_send')

    pre_start  = Signal(providing_args=["router"])
    post_start = Signal(providing_args=["router"])
    pre_stop   = Signal(providing_args=["router"])
    post_stop  = Signal(providing_args=["router"])


    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls(
                prevent=False)

        return cls.__instance


    def __init__(self, prevent=True):

        # since router didn't used to be a singleton, there may be dark places
        # that it's still spawned the usual way. unless specifically asked not
        # to, i'm going to explode here, to avoid violating the expectation that
        # there is only a single router. later, we can remove the argument.
        if prevent:
            raise Exception(
                "Router is a singleton. " +\
                "Use Router.instance() instead.")

        # otherwise, initialize as usual
        self.backends = []
        self.apps = []
        self.logger = None

        self.running = False
        """TODO: Docs"""

        self.accepting = False
        """TODO: Docs"""

        self._queue = Queue.Queue()
        """Pending incoming messages, populated by Router.incoming_message."""


    def __str__(self):

        # there's only ever a single
        # router, so no ambiguity here
        return "Router"


    def _logger_name(self):
        return "rapidsms.router"


    # -------------
    # CONFIGURATION
    # -------------


    def add_backend(self, type, name, config={}):
        """
        Finds a RapidSMS backend class, instantiates and (optionally) configures
        it, and adds it to the list of backends that will be polled for incoming
        messages while it is running. Returns the configured instance, or raises
        ImportError if the module was invalid.

        >>> router = Router.instance()
        >>> backend = router.add_backend(
        ...     "base", "my_mock_backend",
        ...     { "a": "Alpha", "b": "Beta" })

        (The class of the Backend instance is derrived from 'type' by importing
        the '"rapidsms.backends.%s" % (type)' module, and looking for a subclass
        of BackendBase.)

        >>> backend.__class__
        <class 'rapidsms.backends.base.BackendBase'>

        >>> backend.name
        'my_mock_backend'

        >>> backend.config['a']
        'Alpha'
        
        The instance is added to the router's list of backends, and is regularly
        polled for new messages once the router is started.

        >>> backend in router.backends
        True
        
        # TODO: check that the router polls this backend once started. maybe
        # start it in a separate thread. (is this too much for doctest?)
        """

        # backends live in rapidsms/backends/*.py
        # import it early to check that it's valid
        module_name = "rapidsms.backends.%s" % type
        __import__(module_name)

        # find the backend class (regardless of its name). it should
        # be the only subclass of rapidsms.Backend defined the module
        cls = get_class(sys.modules[module_name], BackendBase)

        # instantiate and configure the backend instance.
        # (FYI, i think it's okay to configure backends at
        # startup, since the webui isn't affected by them.
        # (except in a purely informative ("you're running
        # _these_ backends") sense))
        backend = cls(self, name)
        backend._configure(**config)
        self.backends.append(backend)

        return backend


    # TODO: this is a rather ugly public API. replace it with something nicer,
    # like accessing self.backends and self.apps via router['whatever'] (since
    # the names should be unique anyway, although i'm not sure that's enforced)
    def get_backend(self, name):
        """
        Returns the backend named 'name', if it exists, or None.
        """

        for backend in self.backends:
            if backend.name == name:
                return backend

        return None


    def add_app(self, name, conf={}):
        """
        Finds a RapidSMS app class (given its module name), instantiates and
        (optionally) configures it, and adds it to the list of apps that are
        notified of incoming messages. Returns the instance, or None if the app
        module could not be imported.

        This method does too much to doctest.
        TODO: break it up into smaller parts.
        """

        # try to import the .app module from this app. it's okay if the
        # module doesn't exist, but all other exceptions will propagate
        module = try_import("%s.app" % name)
        if module is None:
            return None

        # find the app class (regardless of its name). it should be
        # the only subclass of rapidsms.App defined the app module
        cls = get_class(module, AppBase)

        # instantiate and configure the app instance.
        # TODO: app.configure must die, because the webui (in a separate
        # process) can't access the app instances, only the flat modules
        app = cls(self)
        app._configure(**dict(conf))
        self.apps.append(app)

        return app


    def _wait(self, func, timeout):
        """
        Keep calling 'func' (a lambda function) until it returns True,
        for a maximum of 'timeout' seconds. Return True if 'func' does,
        or False if the timeout is eached.
        """

        for n in range(0, timeout*10):
            if func(): return True
            else: time.sleep(0.1)

        return False


    # -------
    # STARTUP
    # -------


    def start_backend(self, backend):
        while True:
            try:
                started = backend.start()

                # if backend execution completed
                # normally (and did not raise),
                # allow the thread to terminate
                break

            except Exception, err:
                self.exception("Error in the %s backend" % backend)

                # this flows sort of backwards. wait for five seconds
                # (to give the backend a break before retrying), but
                # abort and return if self.accepting is ever False (ie,
                # the router is shutting down). this ensures that we
                # don't delay shutdown, because that causes me to SIG
                # KILL, which prevents things from stopping cleanly
                if self._wait(lambda: not self.accepting, 5):
                    return None

                self.warn("Restarting the %s backend" % backend)



    def start_all_apps (self):
        """Calls the _start_ method of each app registed via
           Router.add_app, logging any exceptions raised, but
           not allowing them to propagate. Returns True if all
           of the apps started without raising."""

        raised = False
        for app in self.apps:
            try:
                app.start()

            except Exception:
                self.log_last_exception("The %s app failed to start" % app)
                raised = True

        # if any of the apps raised, we'll return
        # False, to warn that _something_ is wrong
        return not raised


    def start_all_backends (self):
        """
        Starts all backends registed via Router.add_backend, by calling self.start_backend in a new thread for each."""

        for backend in self.backends:
            worker = threading.Thread(
                target=self.start_backend,
                args=(backend,))

            worker.start()

            # attach the worker thread to the backend,
            # so we can check that it's still running
            backend.thread = worker


    def stop_all_backends (self):
        """Notifies all backends registered via Router.add_backend
           that they should stop. This method cannot guarantee that
           backends *will* stop in a timely manner."""

        for backend in self.backends:
            try:
                backend.stop()
                timeout = 5
                step = 0.1

                # wait up to five seconds for the backend's
                # worker thread to terminate, or log failure
                while(backend.thread.is_alive()):
                    if timeout <= 0:
                        raise RuntimeError, "The %s backend's worker thread did not terminate" % backend

                    else:
                        time.sleep(step)
                        timeout -= step

            except Exception:
                self.log_last_exception("The %s backend failed to stop" % backend)


    def start(self):
        """
        Starts polling the backends for incoming messages, and blocks until a
        KeyboardInterrupt or SystemExit is raised, or Router.stop is called.
        """

        # dump some debug info for now
        #self.info("BACKENDS: %r" % (self.backends))
        #self.info("APPS: %r" % (self.apps))
        self.info("Starting apps and backends...")

        self.pre_start.send(self)
        self.start_all_backends()
        self.start_all_apps()
        self.post_start.send(self)
        self.running = True

        # now that everything is started,
        # we are ready to accept messages
        self.accepting = True

        self.info("Waiting for incoming messages")

        try:
            while self.running:

                # fetch the next pending incoming message, if one is available
                # immediately. this increments the number of "tasks" on the
                # queue, which MUST be decremented later to avoid a deadlock
                # during graceful shutdown (it calls _queue.join to wait for all
                # pending messages to be processed before stopping the backends
                # and terminating). see help(Queue.Queue.task_done) for more.
                try:
                    msg = self._queue.get(block=False)

                    # process the message (which currently (20091005) blocks
                    # until the outgoing responses are all sent), and ensure
                    # that the task counter is decremented
                    self.incoming(msg)
                    self._queue.task_done()

                # if there were no messages waiting, wait a very short (in human
                # terms) time before looping to check again. do this here (rather
                # than every time) to avoid delaying shutdown or the next message
                except Queue.Empty:
                    time.sleep(0.1)

        # stopped via ctrl+c
        except KeyboardInterrupt:
            self.warn("Caught KeyboardInterrupt")

        # stopped via sys.exit
        except SystemExit:
            self.warn("Caught SystemExit")

        # refuse to accept any new messages. the backend(s) might
        # have to throw them away, but at least they can pass the
        # refusal upstream to the device/gateway where possible
        self.accepting = False

        self.info("Stopping...")
        self.stop_all_backends()
        self.running = False


    # ------------------
    # MESSAGE PROCESSING
    # ------------------


    def incoming_message(self, msg):
        """
        Adds 'msg' to the incoming message queue and returns True, or False if
        this router is not currently accepting new messages (either because the
        queue is full, or we are shutting down).

        Adding a message to the queue is no guarantee that it will be processed
        any time soon (although the queue is regularly polled while Router.start
        is blocking), or responded to at all.
        """

        if not self.accepting:
            return False

        try:
            self._queue.put(msg)
            return True

        # if the queue is of a limited size, it may raise the Full
        # exception. there's no sense exploding (especially since
        # we have a bunch of pending messages), so just refuse to
        # accept it. hopefully the backend can in turn refuse it
        except Queue.Full:
            return False


    def stop(self, graceful=False):
        """
        Stops the router, which unblocks the Router.start method as soon as
        possible. This may leave unprocessed messages in the incoming or
        outgoing queues.
        
        If the optional argument 'graceful' is True, this router does its best
        to avoid leaving unprocessed messages around, by refusing to accept new
        incoming messages and blocking (by calling Router.join) until all
        currently pending messages are processed --then stopping.
        """

        if graceful:
            self.accepting = False
            self.join()

        self.running = False



    def join(self):
        """
        Blocks until the incoming message queue is empty. This method can
        potentially block forever, if it is called while this Router is
        accepting incoming messages.
        """

        self._queue.join()
        return True


    def __sorted_apps(self):
        return sorted(self.apps, key=lambda a: a.priority())


    def incoming(self, message):
        """
        Incoming phases:

        Filter:
          The first phase, before any actual work is done. This is the only
          phase that can entirely abort further processing of the incoming
          message, which it does by returning True. (TODO: use an exception
          instead, since this is an exceptional circumstance)

        Parse:
          Don't do INSERTs or UPDATEs in here!

        Handle:
          Respond to messages here.

        Catch:
          Provide a default message. Only a single installed app should have a
          "catch" phase, since app ordering shouldn't be important.

        Cleanup:
          An opportunity to clean up anything started during earlier phases.
        """

        self.info("Incoming message via %s: %s ->'%s'" %\
            (message.connection.backend, message.connection.identity, message.text))

        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it
        try:
            for phase in self.incoming_phases:
                for app in self.__sorted_apps():
                    self.debug("IN %s phase %s" % (phase, app))
                    responses = len(message.responses)
                    handled = False
                    try:
                        handled = getattr(app, phase)(message)
                    except Exception, e:
                        self.error("%s failed on %s: %r\n%s", app, phase, e, traceback.print_exc())

                    # during the "filter" phase, apps can return True
                    # to abort ALL further processing of this message
                    if phase == 'filter':
                        if handled is True:
                            self.warning('Message filtered by "%s" app', app)
                            raise(StopIteration)

                    elif phase == 'handle' or phase == 'catch':
                        if handled is True:
                            self.debug("%s short-circuited %s phase" % (app, phase))
                            break

                    elif responses < len(message.responses):
                        self.warning("App '%s' shouldn't send responses in %s()!", 
                            app.config["type"], phase)

        # maybe raised within the loop, when
        # it's aborted during the filter phase
        except StopIteration:
            pass

        # now send the message's responses
        message.flush_responses()

        # we are no longer interested in
        # this message... but some crazy
        # synchronous backends might be!
        message.processed = True


    def outgoing(self, message):
        self.info("Outgoing message via %s: %s <- '%s'" %\
            (message.connection.backend, message.connection.identity, message.text))
        
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for phase in self.outgoing_phases:
            continue_sending = True
            
            # call outgoing phases in the opposite order of the
            # incoming phases so that, for example, the first app
            # called with an incoming message is the last app called
            # with an outgoing message
            for app in reversed(self.__sorted_apps()):
                self.debug("OUT %s phase %s" % (phase, app))
                
                try:
                    continue_sending = getattr(app, phase)(message)
                except Exception, e:
                    self.error("%s failed on %s: %r\n%s", app, phase, e, traceback.print_exc())
                if continue_sending is False:
                    self.info("App '%s' cancelled outgoing message", app)
                    return False

        # now send the message out
        self.get_backend(message.connection.backend.name).send(message)
        self.debug("SENT message '%s' to %s via %s" % (message.text,\
            message.connection.identity, message.connection.backend))
        return True


# a single instance of the router singleton is available globally,
# like the db connection. it shouldn't be necessary to muck with
# this very often (since most interaction with the Router happens
# within an App or Backend, which have their own .router property),
# but when it is, it should be done via this process global
router = Router.instance()
