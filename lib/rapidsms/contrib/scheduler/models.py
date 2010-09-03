#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models
from fields import PickledObjectField
from django.utils.dates import MONTHS, WEEKDAYS_ABBR

# set timespans (e.g. EventSchedule.hours, EventSchedule.minutes) to 
# ALL when we want to schedule something for every hour/minute/etc.
ALL = '*'
# knowing which fields are related to time is useful
# for a bunch of operations below
# TIME_FIELDS should always reflect the names of 
# the sets of numbers which determine the scheduled time
_TIME_FIELDS = ['minutes', 'hours', 'days_of_week', 
               'days_of_month', 'months']

class EventSchedule(models.Model):
    """ create a new EventSchedule and save it every time 
    you want to register a new event on a schedule
    we can implement one_off future events by setting count to 1 
    All timespans less than the specified one must be set
    i.e. a weekly schedule must also specify which hour, minute, etc.
    However, all timespans greater than the specified one
    default to "all" (as long as one is specified).
    i.e. a weekly schedule will fire every month
    
    callback - all callback function must take as the first 
        argument a reference to a 'router' object
    """
    # whether this schedule is active or not
    callback = models.CharField(max_length=255, 
                                help_text="Name of Python callback function")
    # blank: ensure django validation doesn't force a value
    # null: set db value to be Null
    description = models.CharField(max_length=255, null=True, blank=True)

    # pickled set
    callback_args = PickledObjectField(null=True, blank=True)
    # pickled dictionary
    callback_kwargs = PickledObjectField(null=True, blank=True)
    
    # the following are pickled sets of numbers
    months = PickledObjectField(null=True, blank=True, help_text="'1,2,3' for jan, feb, march - '*' for all")
    days_of_month = PickledObjectField(null=True, blank=True, help_text="'1,2,3' for 1st, 2nd, 3rd - '*' for all")
    days_of_week = PickledObjectField(null=True, blank=True, help_text="'0,1,2' for mon, tue, wed - '*' for all")
    hours = PickledObjectField(null=True, blank=True, help_text="'0,1,2' for midnight, 1 o'clock, 2 - '*' for all")
    minutes = PickledObjectField(null=True, blank=True, help_text="'0,1,2' for X:00, X:01, X:02 - '*' for all")
    
    start_time = models.DateTimeField(null=True, blank=True, 
                                      help_text="When do you want alerts to start? Leave blank for 'now'.")
    end_time = models.DateTimeField(null=True, blank=True, 
                                      help_text="When do you want alerts to end? Leave blank for 'never'.")
    # how many times do we want this event to fire? optional
    count = models.IntegerField(null=True, blank=True, 
                                help_text="How many times do you want this to fire? Leave blank for 'continuously'")
    active = models.BooleanField(default=True)
    
    """
    class Meta:
        permissions = (
            ("can_view", "Can view"),
            ("can_edit", "Can edit"),
        )
    """
    
    # First, we must define some utility classes
    class AllMatch(set):
        """Universal set - match everything"""
        def __contains__(self, item): return True
    allMatch = AllMatch(['*'])

    class UndefinedSchedule(TypeError):
        """ raise this error when attempting to save a schedule with a
        greater timespan specified without specifying the lesser timespans
        i.e. scheduling an event for every hour without specifying what
        minute
        """
        pass

    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        def _set_to_string(set, conversion_dict=None):
            if len(set)>0:
                if conversion_dict is not None:
                    return ", ".join( [unicode(conversion_dict[m]) for m in set] )
                else:
                    return ", ".join( [unicode(m) for m in set] )
            else: 
                return 'All'
        months = _set_to_string(self.months, MONTHS)
        days_of_month = _set_to_string(self.days_of_month)
        days_of_week = _set_to_string(self.days_of_week, WEEKDAYS_ABBR)
        hours = _set_to_string(self.hours)
        minutes = _set_to_string(self.minutes)
        return "%s: Months:(%s), Days of Month:(%s), Days of Week:(%s), Hours:(%s), Minutes:(%s)" % \
            ( self.callback, months, days_of_month, days_of_week, hours, minutes )
            
    def __init__(self, *args, **kwargs):
        # these 3 lines allow users to create eventschedules from arrays
        # and not just sets (since lots of people don't know sets)
        for time in _TIME_FIELDS:
            if time in kwargs and isinstance(kwargs[time],list):
                kwargs[time] = set( kwargs[time] )
        super(EventSchedule, self).__init__(*args, **kwargs)
        if self.callback_args is None: self.callback_args = []
        if self.callback_kwargs is None: self.callback_kwargs = {}
        for time in _TIME_FIELDS:
            if getattr(self, time) is None: 
                setattr(self,time, set())
    
    # TODO: define these helper functions
    # def set_daily(self):
    # def set_weekly(self): etc.
    
    @staticmethod
    def validate(months, days_of_month, days_of_week, hours, minutes):
        """
        The following function doesn't touch data: it just checks 
        for valid boundaries
        
        when a timespan is set, all sub-timespans must also be set
        i.e. when a weekly schedule is set, one must also specify day, hour, and minute.
        """
        EventSchedule.validate_ranges(months, days_of_month, days_of_week, hours, minutes)
        EventSchedule.validate_subtimespans(months, days_of_month, days_of_week, hours, minutes)
        
    @staticmethod
    def validate_ranges(months, days_of_month, days_of_week, hours, minutes):
        EventSchedule.check_minutes_bounds(minutes)
        EventSchedule.check_hours_bounds(hours)
        EventSchedule.check_days_of_week_bounds(days_of_week)
        EventSchedule.check_days_of_month_bounds(days_of_month)
        EventSchedule.check_months_bounds(months)
    
    @staticmethod
    def validate_subtimespans(months, days_of_month, days_of_week, hours, minutes):
        if len(minutes)==0 and len(hours)==0 and len(days_of_week)==0 and \
            len(days_of_month)==0 and len(months)==0:
            raise TypeError("Must specify a time interval for schedule")
        if len(hours)>0 and len(minutes)==0:
            raise EventSchedule.UndefinedSchedule("Must specify minute(s)")
        if len(days_of_week)>0 and len(hours)==0: 
            raise EventSchedule.UndefinedSchedule("Must specify hour(s)")
        if len(days_of_month)>0 and len(hours)==0: 
            raise EventSchedule.UndefinedSchedule("Must specify hour(s)")
        if len(months)>0 and len(days_of_month)==0 and len(days_of_week)==0:
            raise EventSchedule.UndefinedSchedule("Must specify day(s)")

    # we break these out so we can reuse them in forms.py        
    @staticmethod
    def check_minutes_bounds(minutes):
        check_bounds('Minutes', minutes, 0, 59)
    @staticmethod
    def check_hours_bounds(hours):
        check_bounds('Hours', hours, 0, 23)
    @staticmethod
    def check_days_of_week_bounds(days_of_week):
        check_bounds('Days of Week', days_of_week, 0, 6)
    @staticmethod
    def check_days_of_month_bounds(days_of_month):
        check_bounds('Days of Month', days_of_month, 1, 31)
    @staticmethod
    def check_months_bounds(months):
        check_bounds('Months', months, 1, 12)
        
    def save(self, *args, **kwargs):
        """
        
        TODO - still need to fix this so that creating a schedule
        in the ui, saving it, editing it, saving it, editing it continues to work
        with callback_args, kwargs, and different timespans
        (currently fails because set([1,2]) -> a string)
        """
        
        # transform all the input into known data structures
        for time in _TIME_FIELDS:
            val = getattr(self, time)
            if val is None or len(val)==0:
                # set default value to empty set
                setattr(self,time,set())
            if isinstance(val,list):
                # accept either lists or sets, but turn all lists into sets
                val = set(val)
                setattr(self,time,val)
            if not self._valid(getattr(self,time)):
                raise TypeError("%s must be specified as " % time + 
                                "sets of numbers, an empty set, or '*'")
        
        # validate those data structures
        self.validate(self.months, self.days_of_month, self.days_of_week, 
                      self.hours, self.minutes)
        
        super(EventSchedule, self).save(*args, **kwargs)
    
    def should_fire(self, when):
        """Return True if this event should trigger at the specified datetime """
        if self.start_time:
            if self.start_time > when:
                return False
        if self.end_time:
            if self.end_time < when:
                return False
            
        # The internal variables in this function are because allMatch doesn't 
        # pickle well. This would be alleviated if this functionality were optimized
        # to stop doing db calls on every fire
        minutes = self.minutes
        hours = self.hours
        days_of_week = self.days_of_week
        days_of_month = self.days_of_month
        months = self.months
        if self.minutes == '*': minutes = self.allMatch
        if self.hours == '*': hours = self.allMatch
        if self.days_of_week == '*': days_of_week = self.allMatch
        if self.days_of_month == '*': days_of_month = self.allMatch
        if self.months == '*': months = self.allMatch
        
        # when a timespan is set, all super-timespans default to 'all'
        # i.e. a schedule specified for hourly will automatically be sent
        # every day, week, and month.
        if len(months) == 0:
            months=self.allMatch
        if months == self.allMatch:
            if len(days_of_month)==0:
                days_of_month = self.allMatch
            if len(days_of_week)==0:
                days_of_week = self.allMatch
        if len(hours) == 0 and days_of_month==self.allMatch and \
            days_of_week == self.allMatch:
            hours = self.allMatch
        # self.minutes will never be empty
        
        # the following ensures that 'days of month' will override empty 'day of week'
        # and vice versa
        if len(days_of_month)>0 and len(days_of_week)==0:
            days_of_week = self.allMatch
        if len(days_of_week)>0 and len(days_of_month)==0:
            days_of_month = self.allMatch
        
        return ((when.minute     in minutes) and
                (when.hour       in hours) and
                (when.day        in days_of_month) and
                (when.weekday()  in days_of_week) and
                (when.month      in months))

    def activate(self):
        self.active = True
        self.save()
        
    def deactivate(self):
        self.active = False
        self.save()

    def _valid(self, timespan):
        if isinstance(timespan, set) or timespan == '*':
            return True
        return False

############################
# global utility functions #
############################

def set_weekly_event(callback, day, hour, minute, callback_args):
    # relies on all the built-in checks in EventSchedule.save()
    schedule = EventSchedule(callback=callback, hours=set([hour]), \
                             days_of_week=set([day]), minutes=set([minute]), \
                             callback_args=callback_args )
    schedule.save()

def set_daily_event(callback, hour, minute, callback_args):
    # relies on all the built-in checks in EventSchedule.save()
    schedule = EventSchedule(callback=callback, hours=set([hour]), \
                             minutes=set([minute]), \
                             callback_args=callback_args )
    schedule.save()

# check valid values
def check_bounds(name, time_set, min, max):
    if time_set!='*': # ignore AllMatch/'*'
        for m in time_set: # check all values in set
            if int(m) < min or int(m) > max:
                raise TypeError("%s (%s) must be a value between %s and %s" % \
                                (name, m, min, max))
