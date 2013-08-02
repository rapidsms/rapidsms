#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.messagelog.models import Message
import django_filters


class MessageFilter(django_filters.FilterSet):
    """
    A filter for the message log
    """
    connection__identity = django_filters.CharFilter(
        lookup_type='icontains',
        label='Identity',
    )
    text = django_filters.CharFilter(lookup_type='icontains')
    date = django_filters.DateRangeFilter()

    class Meta:
        model = Message
        fields = [
            'connection__identity',
            'text',
            'date',
        ]
