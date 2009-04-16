#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


import datetime
from django.utils.timesince import timesince
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import date as filter_date, time as filter_time

from apps.reporters.models import *


@register.filter()
def magnitude_ago(value):
    """Given a datetime, returns a string containing the
       most appropriate unit to use when describing the
       time since that date, out of: minutes, hours, days,
       months, years."""
    
    # TODO: implement
    return "hours"


@register.filter()
def last_seen(value, autoescape=None):
    """Formats a datetime as an HTML string representing a
       short digest of the time since that date, contained
       by a <span>, with a title (tooltip) of the full date."""
    
    # if autoescaping is on, then we will
    # need to pass outgoing strings through
    # cond_esc, or django will escape the HTML
    if autoescape: esc = conditional_escape
    else:          esc = lambda x: x

    try:
        if value:
            
            # looks like we have a valid date - return
            # a span containing the long and short version
            ts = timesince(value)
            mag = magnitude_ago(value)
            long = "on %s at %s" % (filter_date(value), filter_time(value))
            out = '<span class="last-seen %s" title="%s">%s ago</span>' % (esc(mag), esc(long), esc(ts))
        
        # abort if there is no date (it's
        # probably just a null model field)
        else:
            out = '<span class="last-seen n/a">Never</span>'
    
    # something went wrong! don't blow up
    # the entire template, just flag it
    except (ValueError, TypeError):
        out = '<span class="last-seen error">Error</span>'
    
    return mark_safe(out)
last_seen.needs_autoescape = True


@register.inclusion_tag("reporters/partials/reporters/index.html")
def reporters_index():
    return { "reporters": Reporter.objects.all() }


@register.inclusion_tag("reporters/partials/reporters/form.html")
def reporters_form(reporter=None):
    return {
        "groups":   ReporterGroup.objects.flatten(),
        "backends": PersistantBackend.objects.all(),
        "reporter": reporter
    }

@register.inclusion_tag("reporters/partials/groups/index.html")
def groups_index():
    return { "groups": ReporterGroup.objects.flatten() }


@register.inclusion_tag("reporters/partials/groups/form.html")
def groups_form(reporter=None):
    return { "groups": ReporterGroup.objects.flatten() }


