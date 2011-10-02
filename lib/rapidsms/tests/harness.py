#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os

from django.conf import settings

from rapidsms.router.base import BaseRouter
from rapidsms.backends.base import BackendBase
from ..apps.base import AppBase


class setting(object):
    """
    A context manager for the Django settings module that lets you
    override settings while running tests, e.g.:
    
    with setting(RAPIDSMS_ROUTER='foo.bar.Class'):
        assert_equals(get_router(), foo.bar.Class)
    """

    def __init__(self, **kwargs):
        self.settings = kwargs
        self.saved_settings = {}
        self.default_value = None

    def __enter__(self):
        for k, v in self.settings.items():
            self.saved_settings[k] = getattr(settings, k, self.default_value)
            setattr(settings, k, v)

    def __exit__(self, exc_type, exc_value, traceback):
        for k, v in self.saved_settings.items():
            if v != self.default_value:
                setattr(settings, k, v)


# a really dumb Logger stand-in
class MockLogger (list):
    def __init__(self):
        # enable logging during tests with an
        # environment variable, since the runner
        # doesn't seem to have args
        self.to_console = os.environ.get("verbose", False)

    def write (self, *args):
        if self.to_console:
            if len(args) == 3:
                print args[2]
            else:    
                print args[2] % args[3:]
        self.append(args)

# a subclass of BaseRouter with all the moving parts replaced
class MockRouter (BaseRouter):
    def start (self):
        self.running = True
        self.start_all_backends()
        self.start_all_apps()

    def stop (self):
        self.running = False
        self.stop_all_backends()

class MockBackend (BackendBase):
    """
    A simple mock backend, modeled after the BucketBackend
    """
    def start(self):
        self.bucket = []
        self.outgoing_bucket = []
        BackendBase.start(self)

    def receive(self, identity, text):
        msg = self.message(identity, text)
        self.router.incoming_message(msg)
        self.bucket.append(msg)
        return msg

    def send(self, msg):
        self.bucket.append(msg)
        self.outgoing_bucket.append(msg)
        return True

    def run(self):
        pass
    
    def next_outgoing_message(self):
        if len(self.outgoing_bucket) == 0:
            return None
        return self.outgoing_bucket.pop(0)
 
# a subclass of App with all the moving parts replaced
class MockApp (AppBase):
    def configure (self):
        self.calls = []

    def start (self):
        self.calls.append(("start",))

    def parse (self, message):
        self.calls.append(("parse", message))

    def handle (self, message):
        self.calls.append(("handle", message))

    def cleanup (self, message):
        self.calls.append(("cleanup", message))

    def outgoing (self, message):
        self.calls.append(("outgoing", message))

    def stop (self):
        self.calls.append(("stop",))

class EchoApp (MockApp):
    def handle (self, message):
        MockApp.handle(self, message)
        message.respond(message.peer + ": " + message.text)


class CustomRouter(object):
    """
    Inheritable TestCase-like object that allows Router customization
    """
    router_class = 'rapidsms.router.test.TestRouter'
    router_backends = {}

    def setUp(self):
        super(CustomRouter, self).setUp()
        def update_router(sender, **kwargs):
            for key, backend in self.router_backends.iteritems():
                sender.add_backend(key, backend(sender, key))
        BaseRouter.post_init.connect(update_router, weak=False)
        self._RAPIDSMS_ROUTER = getattr(settings, 'RAPIDSMS_ROUTER', None)
        setattr(settings, 'RAPIDSMS_ROUTER', self.router_class)

    def tearDown(self):
        super(CustomRouter, self).tearDown()
        setattr(settings, 'RAPIDSMS_ROUTER', self._RAPIDSMS_ROUTER)
