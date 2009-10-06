#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time, Queue
from rapidsms.component import Component
from rapidsms.messages.incoming import IncomingMessage


class BackendBase(Component):
    def __init__ (self, router, name):
        self._queue = Queue.Queue()
        self._running = False
        self._router = router
        self._name = name


    @property
    def message_waiting (self):
        """
        Returns the number of incoming messages waiting to be processed.
        """

        return self._queue.qsize()


    def next_message (self):
        """
        Returns the next incoming message waiting to be processed, or None if
        there are none pending. This method should be called regularly by
        """

        try:
            return self._queue.get(False)

        except Queue.Empty:
            return None

    @property
    def name(self):
        return self._name

    @property
    def running (self):
        return self._running

    def start(self):
        self._running = True
        try:
            self.run()
        finally:
            self._running = False

    def run (self):
        while self.running:
            time.sleep(1)

    def stop(self):
        self._running = False


    @property
    def model(self):
        """
        Returns the Django stub model representing this backend in the database.
        Each backend instance 
        """

        from rapidsms.models import Backend as B
        backend, created = B.objects.get_or_create(
            name=self.name)

        return backend


    def message(self, identity, text, received_at=None):

        # imports here, rather than at the top, to
        # give the django orm a chance to initialize
        from rapidsms.models import Connection

        # connections are models now (to simplify lightweight
        # persistance), so fetch an existing instance if we've
        # already heard from this connection, or create one
        conn, created = Connection.objects.get_or_create(
            backend=self.model,
            identity=identity)

        return IncomingMessage(
            conn, text, received_at)


    def route(self, msg):
        return self.router.incoming_message(msg)
