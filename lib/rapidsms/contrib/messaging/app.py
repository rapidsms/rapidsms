#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.apps.base import AppBase
from rapidsms.models import Connection
from rapidsms.messages.outgoing import OutgoingMessage


class App (AppBase):
    """This app receives outgoing messages from the WebUI (via the
       AJAX app), and relays them to the router."""

    PRIORITY = "lowest"

    def ajax_POST_send_message(self, params, form):
        '''
        Sends a message to a connection.  You can call this method
        via the ajax app by posting to the url:
           
            ajax/messaging/send_message
           
        You can also call this directly from a view by calling:
        
            messaging.utils.send_message(connection, text)
        '''
        connection = Connection.objects.get(pk=form["connection_id"])
        return self._send_message(connection, form["text"])
        
    def _send_message(self, connection, message_body):    
        '''Attempts to send a message through a given connection'''
        # attempt to send the message
        # TODO: what could go wrong here?
        msg = OutgoingMessage(connection, message_body)
        return msg.send()
        
