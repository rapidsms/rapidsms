#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.apps.base import AppBase
from .utils import get_handlers


class App(AppBase):
    def start(self):
        """
        Spiders all apps, and registers all available handlers.
        """

        self.handlers = get_handlers()

        if len(self.handlers):
            class_names = [cls.__name__ for cls in self.handlers]
            self.info("Registered: %s" % (", ".join(class_names)))

    def handle(self, msg):
        """
        Forwards the *msg* to every handler, and short-circuits the
        phase if any of them accept it. The first to accept it will
        block the others, and there's deliberately no way to predict
        the order that they're called in. (This is intended to force
        handlers to be as reluctant as possible.)
        """

        for handler in self.handlers:
            if handler.dispatch(self.router, msg):
                self.info("Incoming message handled by %s" % handler.__name__)
                return True
