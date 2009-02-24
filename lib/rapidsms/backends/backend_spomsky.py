#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from backend_base import Base
import spomsky


class Spomsky(Base):
    
    def __init__(self, router, host="localhost", port="8100"):
        self.client = spomsky.Client(host, port)
        self.router = router
