# vim: ai sts=4 ts=4 et sw=4
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from apps.reporters.models import Location, Reporter, PersistantConnection


class NetDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    distributed = models.PositiveIntegerField()
    expected = models.PositiveIntegerField()
    actual = models.PositiveIntegerField()
    discrepancy = models.PositiveIntegerField()


class CardDistribution(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField()
    settlements = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    distributed = models.PositiveIntegerField()

class AirtimePins(models.Model):
    NETWORK_TYPES = (
        ('MTN', 'MTN Nigeria'),
        ('GLO', 'Glo Mobile'),
        ('ZAIN', 'Zain'),
        ('VISAFONE', 'Visafone'),
        ('ETISALAT', 'Etisalat'),
        ('MULTILINKS', 'Multilinks'),
        ('STARCOMMS', 'Starcomms'),
        ('ZOOM', 'Zoom')
    )

    network = models.CharField(blank=True, null=True, max_length=20, choices=NETWORK_TYPES)
    serial_no = models.CharField(blank=True, null=True, max_length=20)
    pin = models.CharField(blank=False, null=False, max_length=14)
    value = models.PositiveIntegerField(null=False, default=0, help_text="Airtime value stored in the airtime pin")
    time_loaded = models.DateTimeField(null=True)
    used = models.BooleanField(null=False, default=False)
    time_used = models.DateTimeField(null=True)
    reporter = models.ForeignKey(Reporter, null=True, blank=True)

    @classmethod
    def get_airtime(klass, network):
        '''Get an unused airtime pincode for a particular network'''
        return klass.objects.filter(used=False,network=network).all()[:1].get()
