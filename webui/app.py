#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import urllib2
import rapidsms
#from reporters.models import ReporterGroup
#import time


class App(rapidsms.App):
    """When the message "webui" is received, attempts to fetch
       the PING_URL via urllib2, and responds to indicate whether
       it was successful. The view doesn't really verify much right
       now, but this is rather useful for checking if everything is
       running, without internet access on either end."""

    MSG_OK           = "WIN: The RapidSMS WebUI is alive and well."
    MSG_NOT_RUNNING  = "FAIL: Couldn't connect to the RapidSMS WebUI."
    MSG_BAD_RESPONSE = "FAIL: The RapidSMS WebUI did not respond correctly."
    PING_URL         = "http://localhost:8000/ping"

    #def start(self):
    #    time.sleep(5)
    #    txt = "Merci pour l'assistance a demain -- RapidSMS Team"
    #    ReporterGroup.objects.get(pk=11).__message__(self.router, txt)

    def handle(self, msg):
        if msg.text.lower() == "ping":
            msg.respond("OK")
            return True

        if msg.text == "webui":
            try:
                urllib2.urlopen(self.PING_URL)
                msg.respond(self.MSG_OK)

            except urllib2.HTTPError:
                msg.respond(self.MSG_BAD_RESPONSE)

            except urllib2.URLError:
                msg.respond(self.MSG_NOT_RUNNING)

    def ajax_GET_test(self, params):
        return ["Hello, World!", params]
