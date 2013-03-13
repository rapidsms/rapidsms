#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.shortcuts import render
from .tables import MessageTable
from .models import Message


def message_log(request):
    messages_table = MessageTable(Message.objects.all(),
            template="django_tables2/bootstrap-tables.html")
    messages_table.paginate(page=request.GET.get('page', 1), per_page=10)
    return render(request, "messagelog/index.html", {
        "messages_table": messages_table,
    })
