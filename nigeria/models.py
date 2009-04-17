from django.db import models
from apps.reporters.models import Location, Reporter


# Create your Django models here, if you need them.

class NetDistribution(models.Model):
    reporter = models.ForeignKey(Reporter)
    location = models.ForeignKey(Location)
    distributed = models.PositiveIntegerField()
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    discrepancy = models.PositiveIntegerField()


class CardDistribution(models.Model):
    reporter = models.ForeignKey(Reporter)
    location = models.ForeignKey(Location)
    settlements = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField()
