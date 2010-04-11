#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.templatetags.tabs_tags import register_tab
from rapidsms.utils import render_to_response
from .models import Message
from .tables import Table, Column


class MessagelogTable(Table):
    text      = Column("Text")
    direction = Column("Direction")
    who       = Column("To/From", sortable=False)
    date      = Column("Date")

    def get_query_set(self):
        return Message.objects.all()


@register_tab
def message_log(req):
    return render_to_response(req,
        "logger/index.html", {
            "table": MessagelogTable(req)
        })
