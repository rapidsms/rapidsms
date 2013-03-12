#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.messagelog.models import Message
import django_tables2 as tables


class MessageTable(tables.Table):

    class Meta:
        model = Message
        exclude = ('id', )
        order_by = ('-date', )
