#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Client:
    def __init__(self, host="localhost", port="8100"):
        self.host = host
        self.port = port

    def __repr__(self):
        return '<rapidsms.spomsky.Client host="%s", port="%s">' % (self.host, self.port)
