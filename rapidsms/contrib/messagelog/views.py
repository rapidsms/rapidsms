#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.shortcuts import render
from rapidsms.contrib.messagelog.tables import MessageTable
from rapidsms.contrib.messagelog.models import Message
from rapidsms import settings
from django_tables2 import RequestConfig


def message_log(request):
    messages_table = MessageTable(Message.objects.all(),
            template="django_tables2/bootstrap-tables.html")
    RequestConfig(request, paginate={"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}).configure(messages_table)
    return render(request, "messagelog/index.html", {
        "messages_table": messages_table,
    })
