#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils.safestring import mark_safe

import django_tables2 as tables

from .models import HttpTesterMessage


class MessageTable(tables.Table):

    def render_identity(self, record):
        # Render the phone number with a double arrow pointing to it
        # or away from it, depending on whether the message was going
        # out or coming in.
        if record.direction == HttpTesterMessage.INCOMING:
            return mark_safe(record.identity + "&raquo;")
        else:
            return mark_safe(record.identity + "&laquo;")

    class Meta:
        model = HttpTesterMessage
        sequence = ('date', 'identity', 'text')
        exclude = ('id', 'direction')
        order_by = ('-date', )
        attrs = {'id': 'log'}
