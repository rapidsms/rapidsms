# vim: ai sts=4 ts=4 et sw=4
import re
from django.db import models
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

    def __unicode__(self):
        return "%s (%s) %s" % (self.location, self.reporter, self.time)
    
    @staticmethod
    def get_totals(location):
        all = NetDistribution.objects.all().filter(location=location)
        distributed = 0
        expected = 0
        actual= 0
        discrepancy = 0
        for report in all:
            distributed += report.distributed
            expected += report.expected
            actual += report.actual
            discrepancy += report.discrepancy 
        return {"distributed":distributed, 
                "expected":expected,
                "actual":actual,
                "discrepancy":discrepancy }
        

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
    def get_totals(location):
        all = CardDistribution.objects.all().filter(location=location)
        settlements = 0
        people = 0
        distributed= 0
        for report in all:
            settlements += report.settlements
            people += report.people
            distributed += report.distributed
        return {"settlements":settlements, 
                "people":people,
                "distributed":distributed
    }
                

# this is a signal that says that whenever a location is loaded,
# if these models have also been loaded we should try to set the 
# data for nets and net cards distributed in that location
def loc_nets_cards_post_init(sender, **kwargs):
    """Location post init signal that reads the net and net card information from the 
       models and sets it in the location object, if it is defined"""
    instance = kwargs["instance"]
    instance.net_data =  NetDistribution.get_totals(instance)
    instance.card_data =  CardDistribution.get_totals(instance)
    

# this is the magic that glues the signal to the post load call
models.signals.post_init.connect(loc_nets_cards_post_init, sender=Location)

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

    @classmethod
    def vend_airtime(klass, phone_number):
        '''Lookup the phone_number from available networks and vend a spare airtime pin for the number'''
        for network in klass.NETWORK_TYPES:
            if re.match(network[1], phone_number):
                return klass.get_airtime(network[0])
                break
