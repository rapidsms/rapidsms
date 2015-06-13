#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import logging

from rapidsms.apps.base import AppBase
from .utils import get_handlers


logger = logging.getLogger(__name__)


class App(AppBase):

    def __init__(self, *args, **kwargs):
        """
        Spiders all apps, and registers all available handlers.
        """
        super(App, self).__init__(*args, **kwargs)
        self.handlers = get_handlers()
        if len(self.handlers):
            class_names = [cls.__name__ for cls in self.handlers]
            logger.info("Registered: %s", ", ".join(class_names))

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
                logger.info("Incoming message handled by %s", handler.__name__)
                return True
