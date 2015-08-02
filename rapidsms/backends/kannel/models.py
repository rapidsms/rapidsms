from __future__ import unicode_literals

from django.db import models


STATUS_CHOICES = (
    (1, 'Delivery Success'),
    (2, 'Delivery Failure'),
    (4, 'Message Buffered'),
    (8, 'SMSC Submit'),
    (16, 'SMSC Reject'),
)


class DeliveryReport(models.Model):
    """
    Model to track Kannel delivery reports.
    http://kannel.org/download/1.5.0/userguide-1.5.0/userguide.html#DELIVERY-REPORTS
    """
    date = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateTimeField()
    message_id = models.CharField("Message ID", max_length=255)
    identity = models.CharField(max_length=100)
    sms_id = models.CharField("SMS ID", max_length=36)
    smsc = models.CharField("SMSC", max_length=255)
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    status_text = models.CharField(max_length=255)
