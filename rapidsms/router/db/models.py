from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now

from rapidsms.models import Connection


DIRECTION_CHOICES = (
    ('I', "Incoming"),
    ('O', "Outgoing"),
)

STATUS_CHOICES = (
    ('Q', "Queued"),
    ('R', "Received"),
    ('P', "Processing"),
    ('S', "Sent"),
    ('D', "Delivered"),
    ('E', "Errored")
)


@python_2_unicode_compatible
class Message(models.Model):
    #: Required. See :ref:`message-status-values`.
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='Q', db_index=True)
    #: Required. Date/time when message was created.
    date = models.DateTimeField(auto_now_add=True)
    #: Required. Last date/time the message was updated.
    updated = models.DateTimeField(auto_now=True, null=True, db_index=True)
    #: Date/time when all associated transmissions were sent.
    sent = models.DateTimeField(null=True, blank=True)
    #: Date/time when all associated transmissions were delivered (requires backend functionality).
    delivered = models.DateTimeField(null=True, blank=True)
    #: Required. Either ``'I'`` or ``'O'``.
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES,
                                 db_index=True)
    #: Required. Message text.
    text = models.TextField()
    #: Optional. ID of message as defined by the associated backend.
    external_id = models.CharField(max_length=1024, blank=True)
    #: Optional. Foreign key to ``Message`` that generated this reply.
    in_response_to = models.ForeignKey('self', related_name='responses',
                                       null=True, blank=True)

    def set_status(self):
        if self.direction == 'O':
            if self.transmissions.filter(status='E').exists():
                self.status = 'E'
            elif self.transmissions.exclude(status__in=['S', 'D']).exists():
                self.status = 'P'
            elif self.transmissions.exclude(status__in=['D']).exists():
                self.status = 'S'
                self.sent = now()
            else:
                self.status = 'D'
                self.delivered = now()
        else:
            if self.transmissions.filter(status='E').exists():
                self.status = 'E'
            elif self.transmissions.exclude(status__in=['R']).exists():
                self.status = 'Q'
            else:
                self.status = 'R'
        self.updated = now()
        self.save()
        return self.status

    def __str__(self):
        return self.text[:60]


@python_2_unicode_compatible
class Transmission(models.Model):
    #: Required. Foreign key to associated ``Message``.
    message = models.ForeignKey(Message, related_name='transmissions')
    #: Required. Foreign key to associated ``Connection``.
    connection = models.ForeignKey(Connection, related_name='transmissions')
    #: Required. See :ref:`message-status-values`.
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              db_index=True)
    #: Required. Date/time when transmission was created.
    date = models.DateTimeField(auto_now_add=True)
    #: Required. Last date/time when transmission was updated.
    updated = models.DateTimeField(auto_now=True, null=True, db_index=True)
    #: Date/time when transmission was sent.
    sent = models.DateTimeField(null=True, blank=True)
    #: Date/time when transmission was delivered (requires backend functionality).
    delivered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%d: %s" % (self.pk, self.get_status_display())
