import datetime

from django.db import models, connections

from rapidsms.models import Contact, Connection


DIRECTION_CHOICES = (
    ('I', "Incoming"),
    ('O', "Outgoing"))

STATUS_CHOICES = (
    ('R', "Received"),
    ('H', "Handled"),

    ('P', "Processing"),
    ('L', "Locked"),

    ('Q', "Queued"),
    ('S', "Sent"),
    ('D', "Delivered"),

    ('C', "Cancelled"),
    ('E', "Errored")
)


class Message(models.Model):
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='Q')
    date = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES)
    text = models.TextField()
    external_id = models.CharField(max_length=1024, blank=True)
    in_response_to = models.ForeignKey('self', related_name='responses',
                                       null=True, blank=True)

    def __unicode__(self):
        return self.text[:60]


class Transmission(models.Model):
    message = models.ForeignKey(Message, related_name='transmissions')
    connection = models.ForeignKey(Connection, related_name='transmissions')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    sent = models.DateTimeField(null=True, blank=True)
    delivered = models.DateTimeField(null=True, blank=True)
