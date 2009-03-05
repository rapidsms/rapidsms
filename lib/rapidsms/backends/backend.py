#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms.component
import Queue

class Backend(rapidsms.component.Component):
    def __init__ (self, router):
        self.router     = router
        self._running   = False
        # do we want to put a limit on the queue size?
        # and what do we do if the queue gets full?
        self._queue     = Queue.Queue()

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
        raise NotImplementedError
    
    def stop(self):
        self._running = False
    
    def send(self, message):
        # block until we can add to the queue.
        # it shouldn't be that long.
        self._queue.put(message, True)
    
    def receive(self, caller, text):
        # turn the caller/text into a message object
        msg = Message(self, caller, text)
        # and send it off to the router
        self.router.incoming(msg)
    
    @property
    def has_outgoing (self):
        return self._queue.qsize()
 
    def outgoing (self):
        try:
            return self._queue.get_nowait()
        except Queue.Empty:
            return None
