#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms import tables
from .models import Message


class MessagelogTable(tables.ModelTable):
    
    class Meta:
        model = Message
        exclude = ['id']
        order_by = '-date'