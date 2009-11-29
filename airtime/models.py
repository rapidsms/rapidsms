from django.db import models
from reporters.models import PersistantConnection
import re

class AirtimePins(models.Model):
    '''Store all available Nigerian mobile networks. Still incomplete.'''
    NETWORK_TYPES = (
        ('MTN', '^(\+?234|0)(703|706|803|806)\d{7}$'),
        ('GLO', '^(\+?234|0)(705|805|807)\d{7}$'),
        ('ZAIN', '^(\+?234|0)(708|802|808)\d{7}$'),
        ('VISAFONE', '^(\+?234|0)(7040)\d{6}$'),
        ('ETISALAT', '^(\+?234|0)(809)\d{7}$'),
        ('MULTILINKS', '^(\+?234|0)(7027)\d{6}$'),
        ('STARCOMMS', '^(\+?234|0)(181[26])\d{4}$'),
    )

    network = models.CharField(null=False, max_length=20, choices=NETWORK_TYPES)
    serial_no = models.CharField(blank=True, null=True, max_length=20)
    pin = models.CharField(blank=False, null=False, max_length=14)
    value = models.PositiveIntegerField(null=False, default=0, help_text="Airtime value stored in the airtime pin")
    time_loaded = models.DateTimeField(null=True)
    used = models.BooleanField(null=False, default=False)
    time_used = models.DateTimeField(null=True)
    connection = models.ForeignKey(PersistantConnection, null=True)

    @classmethod
    def get_airtime(klass, network):
        '''Get an unused airtime pincode for a particular network'''
        return klass.objects.filter(used=False,network=network).all()[:1].get()

    @classmethod
    def vend_airtime(klass, phone_number):
        '''Lookup the phone_number from available networks and vend a spare airtime pin for the number'''
        for network in klass.NETWORK_TYPES:
            if re.match(network[1], phone_number):
                return klass.get_airtime(network[0])
                break
