#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from rapidsms.models import Connection
from rapidsms.messages.outgoing import OutgoingMessage


class App (rapidsms.App):
    """This app receives outgoing messages from the WebUI (via the
       AJAX app), and relays them to the router."""

    PRIORITY = "lowest"

    def ajax_POST_send_message(self, params, form):
        '''Sends a message to a connection'''
        connection = Connection.objects.get(pk=form["connection_id"])
        return self._send_message(connection, form["text"])
        
    def _send_message(self, connection, message_body):    
        '''Attempts to send a message through a given connection'''
        # abort if we can't find a valid backend. Backend
        # objects SHOULD refer to a valid RapidSMS backend (via their
        # slug), but sometimes backends are removed or renamed.
        
        # attempt to send the message
        # TODO: what could go wrong here?
        msg = OutgoingMessage(connection, message_body)
        return msg.send()
        
