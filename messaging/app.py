#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from apps.reporters.models import *


class App (rapidsms.app.App):
    def ajax_POST_send_message(self, params, form):
        rep = Reporter.objects.get(pk=form["uid"])
        pconn = rep.connection()

        # abort if we don't know where to send the message to
        # (if the device the reporter registed with has been
        # taken by someone else, or was created in the WebUI)
        if pconn is None:
            raise Exception("%s is unreachable (no connection)" % rep)

        # attempt to send the message
        # TODO: what could go wrong here?
        be = self.router.get_backend(pconn.backend.slug)
        return be.message(pconn.identity, form["text"]).send()

    def start(self):
        # regex to match @alias or @pk
        self.alias_pattern= re.compile("(\s*@\w+\s*)")
        # TODO #grouptitle

    def handle(self, message):
        # FIXME this is a crappy rough draft
        router = self.router
        # gather possible @aliases and @pks occuring in message's text
        possible_reportees = re.finditer(self.alias_pattern, message.text)
        response = ''
        win = []
        fail = []
        for possible_reportee in possible_reportees:
            # pull the @alias or @pk from the match object
            raw_reportee = possible_reportee.group(0)
            # lookup the alias or pk
            reportee = Reporter.lookup(raw_reportee.replace('@','').strip())
            if reportee:
                # TODO only say its a success if its successful
                #if reportee.send(router, message):
                reportee.send(router, message)
                # add to list of successes
                win.append(raw_reportee)
            else:
                # add to list of failures
                fail.append(raw_reportee)
        if len(win) > 0:
            response = response + "Message sent to %s." % (', '.join(win))
        if len(fail) > 0:
            response = response + "No user found for %s." % (', '.join(fail))
        # respond with successes and failures
        return message.respond(response)

