#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from .base import BackendBase


class BucketBackend(BackendBase):
    def start(self):
        self.bucket = []
        BackendBase.start(self)

    def receive(self, identity, text):
        msg = self.message(identity, text)
        self.router.incoming_message(msg)
        self.bucket.append(msg)
        return msg

    def send(self, msg):
        self.bucket.append(msg)
        return True
