#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.paginator import QuerySetPaginator
from rapidsms.utils import render_to_response
from .tables import MessagelogTable


MESSAGES_PER_PAGE = 100


def message_log(req):
    message_table = MessagelogTable(request=req)
    message_table.paginate(QuerySetPaginator, MESSAGES_PER_PAGE,
                           page=req.GET.get('page', 1))
    return render_to_response(req,
        "messagelog/index.html", {
            "messages": message_table,
        })
