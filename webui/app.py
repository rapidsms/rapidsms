#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import urllib2

class App(rapidsms.app.App):
    """When the message "webui" is received, attempts to fetch
       the PING_URL via urllib2, and responds to indicate whether
       it was successful. The view doesn't really verify much right
       now, but this is rather useful for checking if everything is
       running, without internet access on either end."""

    MSG_OK           = "WIN: The RapidSMS WebUI is alive and well."
    MSG_NOT_RUNNING  = "FAIL: Couldn't connect to the RapidSMS WebUI."
    MSG_BAD_RESPONSE = "FAIL: The RapidSMS WebUI did not respond correctly."
    PING_URL         = "http://localhost:8000/ping"

    def configure(self, anon_perms=None):
        # permissions for anonymous (not logged-in) users.
        # bednets and other tabs can be displayed on the dashboard so that visitors will 
        # know that more functionality exists and that they need login creds to access them
        # BUT we are able to keep things like 'reporters & groups', 'messaging', 'training',
        # etc hidden from view
        #
        # otherwise django auth/permissions would only allow us to have all-or-none
        # control of what anonymous users can see.
        #
        # anon_perms should be defined in the webui section of rapidsms.ini
        # like:
        # anon_perms = ['bednets.can_view', 'ipds.can_view']
        self.anon_perms = anon_perms

    def handle(self, msg):
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
