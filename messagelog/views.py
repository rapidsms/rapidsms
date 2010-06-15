#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.utils import render_to_response
from .tables import MessageTable
from .models import Message


def message_log(req):
    return render_to_response(req,
        "messagelog/index.html", {
            "messages_table": MessageTable(Message.objects.all(), request=req)
        })
