#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils.safestring import mark_safe
import django_tables2 as tables
from rapidsms.contrib.messagelog.models import Message
from rapidsms.backends.database.models import INCOMING


class MessageTable(tables.Table):
    def render_direction(self, record):
        if record.direction == INCOMING:
            return mark_safe("<span class='arrow-left'>&larr;</span>")
        else:
            return mark_safe("<span class='arrow-right'>&rarr;</span>")

    class Meta:
        model = Message
        exclude = ('id', )
        order_by = ('-date', )
