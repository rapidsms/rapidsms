from django.db import models

# Create your models here.
class Message(models.Model):
    phone_number = models.CharField(max_length=15)
    date = models.DateTimeField('date published')
    body = models.TextField()
    outgoing = models.BooleanField(default=False)
    
    def __unicode__(self):
        type = "incoming"
        if self.outgoing:
            type = "outgoing"
        return self.phone_number + ":  " + self.body +  "(" + type + " at " + self.date.__str__() + ")" 

