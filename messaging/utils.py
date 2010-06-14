#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.ajax.utils import call_router

def send_message(connection, text):
    """
    Send a message from the webui process to the router process,
    via the ajax app.
    """
    return call_router("messaging", "send_message", 
                       **{"connection_id": connection.id, "text": text })
    