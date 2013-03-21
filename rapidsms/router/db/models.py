from django.db import models
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


class Message(models.Model):
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='Q', db_index=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True, db_index=True)
    sent = models.DateTimeField(null=True, blank=True)
    delivered = models.DateTimeField(null=True, blank=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES,
                                 db_index=True)
    text = models.TextField()
    external_id = models.CharField(max_length=1024, blank=True)
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

    def __unicode__(self):
        return self.text[:60]


class Transmission(models.Model):
    message = models.ForeignKey(Message, related_name='transmissions')
    connection = models.ForeignKey(Connection, related_name='transmissions')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              db_index=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True, db_index=True)
    sent = models.DateTimeField(null=True, blank=True)
    delivered = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "%d: %s" % (self.pk, self.get_status_display())
