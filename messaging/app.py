#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import datetime
import rapidsms
from models import *


class App (rapidsms.App):
    """When an incoming message is received, this application is notified
       last, to grab and log the message as a "free-text" message, to be
       displayed in the WebUI with no automatic response from RapidSMS.

       Also, this app receives outgoing messages from the WebUI (via the
       AJAX app), and relays them to the router."""

    PRIORITY = "lowest"


    def configure(self, catch_all, **kwargs):
        self.catch_all = catch_all


    def catch(self, msg):
        if self.catch_all and not msg.responses:

            # log the message, along with the identity
            # information provided by reporters.app/parse
            msg = IncomingMessage.objects.create(
                received=datetime.datetime.now(),
                text=msg.text,
                **msg.persistance_dict)

            self.info("Message %d captured" % (msg.pk))

            # short-circuit, since this message is dealt
            # with now (even if it shouldn't have been)
            return True


    # NOTE: outgoing messages are not logged here via the "outoging"
    # hook, since we're not interested in ALL outgoing messages; only
    # those that were sent from within the messaging UI (below)


    def ajax_POST_send_message(self, params, form):
        rep = Reporter.objects.get(pk=form["uid"])

        # if this message contains the same text as the _previous_ message sent,
        # and is within 6 hours, we'll recycle it (since it has-many recipients)
        try:
            time_limit = datetime.datetime.now() - datetime.timedelta(hours=6)
            msg = OutgoingMessage.objects.filter(
                sent__gt=time_limit,
                text=form["text"])[0]

        # no match, so create a new outgoing message for
        # this recipient (it might be the first of many)
        except IndexError:
            msg = OutgoingMessage.objects.create(
                sent=datetime.datetime.now(),
                text=form["text"])

        # attach this recipient to
        # the (old or new) message
        msg.recipients.create(
            reporter=rep)

        # abort if we don't know where to send the message to
        # (if the device the reporter registed with has been
        # taken by someone else, or was created in the WebUI)
        pconn = rep.connection()
        if pconn is None:
            raise Exception("%s is unreachable (no connection)" % rep)

        # abort if we can't find a valid backend. PersistantBackend
        # objects SHOULD refer to a valid RapidSMS backend (via their
        # slug), but sometimes backends are removed or renamed.
        be = self.router.get_backend(pconn.backend.slug)
        if be is None:
            raise Exception(
                "No such backend: %s" %
                pconn.backend.title)

        # attempt to send the message
        # TODO: what could go wrong here?
        return be.message(pconn.identity, form["text"]).send()
