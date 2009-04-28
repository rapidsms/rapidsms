from django.db import models

class IncomingMessage(models.Model):
    INCOMING_STATUS_TYPES = (
        ('R', 'Received'), # when the message is first received
        ('H', 'Handling'), # when the router begins processing the message
        ('P', 'Processed'), # when the router has completed processing the message
        ('T', 'Timeout'), # we sent it for processing but it timed out
        ('E', 'Error'), # something went wrong
    )
    phone = models.CharField(max_length=100)
    time = models.DateTimeField()
    text = models.CharField(max_length=160)
    status = models.CharField(max_length=1, choices=INCOMING_STATUS_TYPES)
    responses = models.ManyToManyField("OutgoingMessage")
    
    @property 
    def processed(self):
        return self.status == "P"
    
    def __unicode__(self):
        return "%s > %s" % (self.phone, self.text)

class OutgoingMessage(models.Model):
    OUTGOING_STATUS_TYPES = (
        ('R', 'Received'), # when the message is first submitted by the router
        ('P', 'Processed'), # when the message has been sent back to the user
        ('E', 'Error'), # something went wrong
    )
    phone = models.CharField(max_length=100)
    time = models.DateTimeField()
    text = models.CharField(max_length=160)
    status = models.CharField(max_length=1, choices=OUTGOING_STATUS_TYPES)
    
    def __unicode__(self):
        return "%s < %s" % (self.phone, self.text)

