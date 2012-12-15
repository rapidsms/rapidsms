#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django import forms
from rapidsms.contrib.scheduler.models import EventSchedule

class ScheduleForm(forms.ModelForm):
    """ This form is used to edit existing schedules """
    
    class Meta:
        model = EventSchedule
        fields = ('description', 'months', 'days_of_month',
                  'days_of_week', 'hours', 'minutes', 'count', 'active')
    
    def _format_set(self, value):
        if isinstance( value, basestring) and len(value)>0:
            # The following is necessary to support creating schedules
            # from the admin ui
            if value == "":
                # django admin annoyingly translates
                # its own python object as string
                value = set([])
            else:
                try:
                    # we accept the strings of the form '1,2,3'
                    # which we get from the admin ui
                    value = value.strip(',').split(',')
                    value = set([int(i) for i in value])
                except Exception, e:
                    raise forms.ValidationError("Poorly formatted. " + \
                        "Please enter values as a comma-separated list, " + 
                        "e.g. '1, 2, 3'")
            value = set(value)
        return value
    
    # by making these separate functions, django takes care of reporting
    # all the errors from each field at the same time. These functions:
    # 1. convert strings to the expected data structures
    def clean_minutes(self):
        return self._format_set_and_check_bounds(self.cleaned_data['minutes'], 
                                                 'minutes')
    def clean_hours(self):
        return self._format_set_and_check_bounds(self.cleaned_data['hours'], 
                                                 'hours')
    def clean_days_of_week(self):
        return self._format_set_and_check_bounds(self.cleaned_data['days_of_week'], 
                                                 'days_of_week')
    def clean_days_of_month(self):
        return self._format_set_and_check_bounds(self.cleaned_data['days_of_month'], 
                                                 'days_of_month')
    def clean_months(self):
        return self._format_set_and_check_bounds( self.cleaned_data['months'], 
                                                  'months')
    def _format_set_and_check_bounds(self, value, name):
        value = self._format_set(value)
        check_bounds_func = getattr(EventSchedule, 'check_%s_bounds' % name)
        try:
            check_bounds_func(value)
        except Exception, e:
            raise forms.ValidationError(unicode(e))
        return value

    """
    # The following 4 lines is also to support creating schedules from the admin ui
    # they have been removed because we do not currently support modifying 
    # args and kwargs from the UI
    if self.cleaned_data['callback_args'] and \
      isinstance(self.cleaned_data['callback_args'], basestring):
        self.cleaned_data['callback_args'] = \
          _string_to_array(self.cleaned_data['callback_args'])
    if self.cleaned_data['callback_kwargs'] and \
      isinstance(self.cleaned_data['callback_kwargs'], basestring):
        self.cleaned_data['callback_kwargs'] = \
          _string_to_dictionary(self.cleaned_data['callback_kwargs'])
    """
    
    def clean(self):
        # validate inputs
        if not self.cleaned_data.get('minutes') and \
          not self.cleaned_data.get('hours') and \
          not self.cleaned_data.get('days_of_week') and \
          not self.cleaned_data.get('days_of_month') and \
          not self.cleaned_data.get('months'):
              raise forms.ValidationError("Must specify a time interval for schedule")
        if self.cleaned_data.get('hours') and \
          not self.cleaned_data.get('minutes'):
            raise forms.ValidationError("Must specify minute(s)")
        if self.cleaned_data.get('days_of_week') and \
          not self.cleaned_data.get('hours'): 
            raise forms.ValidationError("Must specify hour(s)")
        if self.cleaned_data.get('days_of_month') and \
          not self.cleaned_data.get('hours'): 
            raise forms.ValidationError("Must specify hour(s)")
        if self.cleaned_data.get('months') and \
          not self.cleaned_data.get('days_of_month') and \
          not self.cleaned_data.get('days_of_week'):
            raise forms.ValidationError("Must specify day(s)")
        return self.cleaned_data

############################
# global utility functions #
############################

def _string_to_array(string):
    return string.strip(',').split(',')

def _string_to_set(string):
    return set(_string_to_array(string))

def _string_to_dictionary(string):
    raise NotImplementedError

