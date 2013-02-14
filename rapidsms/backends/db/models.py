from django.db import models


DIRECTION_CHOICES = (
    ('I', "Incoming"),
    ('O', "Outgoing"),
)


class BackendMessage(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=1, choices=DIRECTION_CHOICES,
                                 db_index=True)
    message_id = models.CharField(max_length=64)
    external_id = models.CharField(max_length=64, blank=True)
    identity = models.CharField(max_length=100)
    text = models.TextField()

    def __unicode__(self):
        return self.text[:60]
