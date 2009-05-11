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
    def get_totals(location):
	'''This is definitely a hack. We really shouldn't use startswith with 
the locations. Doing it otherwise will require recursion which is way overkill and can be hurting performancewise. We should investigate tree structures.'''
        all = NetDistribution.objects.all().filter(location__code__startswith=location.code)
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
        all = CardDistribution.objects.all().filter(location__code__startswith=location.code)
        settlements = 0
        people = 0
        distributed= 0
        time_data = []
        index = 1
        same_day = 0
        for report in all:
            settlements += report.settlements
            people += report.people
            distributed += report.distributed
            #TODO: Complete the commented lines below. This is used to generate the time-sensitive plots for bednets and netcards distribution
#            if str(location.type) == 'LGA' or str(location.type) == 'State' or str(location.type) == 'Ward' and int(taim.mktime(report.time.timetuple())) != same_day:
 #               ud_time = str(taim.mktime(report.time.timetuple()))
  #              time_data.append([ud_time[0:ud_time.find(".")]+"000", int(distributed)])
            index +=1
#TODO: Remove the comment below
            #same_day = int(taim.mktime(report.time.timetuple()))
        return {"settlements":settlements, 
                "people":people,
                "distributed":distributed
   #TODO: uncomment this...and include comma before it.
                #"time_info":time_data
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

