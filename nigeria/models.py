# vim: ai sts=4 ts=4 et sw=4
from django.db import models
from apps.reporters.models import Location, Reporter, PersistantConnection
import time as taim

class NetDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    distributed = models.PositiveIntegerField()
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    discrepancy = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s) %s" % (self.location, self.reporter, self.time)

    @staticmethod
    def net_data(location):
        all = NetDistribution.objects.all().filter(location__pk=location.pk)

        return {"distributed": sum(all.values_list("distributed", flat=True)), 
                "expected": sum(all.values_list("expected", flat=True)),
                "actual": sum(all.values_list("actual", flat=True)),
                "discrepancy": sum(all.values_list("discrepancy", flat=True))}

    
class CardDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    settlements = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s (%s) %s" % (self.location, self.reporter, self.time)
    
    @staticmethod
    def card_data(location):
        all = CardDistribution.objects.all().filter(location__pk=location.pk)

        return {"distributed": sum(all.values_list("distributed", flat=True)), 
                "settlements": sum(all.values_list("settlements", flat=True)),
                "people": sum(all.values_list("people", flat=True))}
