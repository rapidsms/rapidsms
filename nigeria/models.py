from django.db import models
from apps.reporters.models import Location, Reporter


class NetDistribution(models.Model):
    reporter = models.ForeignKey(Reporter)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    distributed = models.PositiveIntegerField()
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    discrepancy = models.PositiveIntegerField()


class CardDistribution(models.Model):
    reporter = models.ForeignKey(Reporter)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    settlements = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField()
