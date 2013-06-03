#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django_tables2 as tables
from rapidsms.contrib.messagelog.models import Message


class MessageTable(tables.Table):

    class Meta:
        model = Message
        exclude = ('id', )
        order_by = ('-date', )
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }
