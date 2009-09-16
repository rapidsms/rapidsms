#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib.apps.handlers import PatternHandler


class RemindHandler(PatternHandler):
    """
    """

    pattern = r"who\s*am\s*i\??"

    def handle(self):
        if self.msg.reporter:
            self.respond("I think you are %s." % self.msg.reporter)

        else:
            self.respond("I don't know who you are.")
