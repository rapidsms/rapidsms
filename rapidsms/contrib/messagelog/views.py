#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rapidsms.contrib.messagelog.tables import MessageTable
from rapidsms.contrib.messagelog.models import Message
from rapidsms.contrib.messagelog.filters import MessageFilter
from rapidsms import settings

from django_tables2 import RequestConfig


@login_required
def message_log(request):
    qset = Message.objects.all()
    qset = qset.select_related('contact', 'connection__backend')
    template = "django_tables2/bootstrap-tables.html"

    message_filter = MessageFilter(request.GET, queryset=qset)
    messages_table = MessageTable(message_filter, template=template)

    paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
    RequestConfig(request, paginate=paginate).configure(messages_table)

    return render(request, "messagelog/index.html", {
        "messages_table": messages_table,
        "message_filter": message_filter,
    })
