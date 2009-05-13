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




class SelfLinkNode(template.Node):
    def __init__(self, *args):
        self.args = args

    def render(self, context):
        
        # resolve all arguments to their
        # values in the current context
        args = [template.resolve_variable(arg, context) for arg in self.args]
        
        # the output defaults to exactly the same url as we're
        # currently viewing, including the GET parameters
        kwargs = context["request"].GET.copy()
        
        # iterate the arguments to this token,
        # which come in pairs of: K,V,K,V,K,V
        while len(args):
            k = args.pop(0)
            v = args.pop(0)
            kwargs[k] = v
        
        # rebuild the new url: same as we're currently
        # viewing, with some GET arguments overridden
        return "%s?%s" % (context["request"].path, kwargs.urlencode())


@register.tag
def self_link(parser, token):
    args = token.split_contents()
    tag_name = args.pop(0)
    
    # this requires an even number of args, so they
    # can be converted into a dict without ambiguity
    if len(args) % 2:
        raise template.TemplateSyntaxError,\
            "The {%% %s %%} tag requires an even number of arguments" % (tag_name)

    return SelfLinkNode(*args)




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
    data = {
        "all_groups": ReporterGroup.objects.flatten()
    }
    
    if reporter:
        data["connections"] = reporter.connections.all()
        data["groups"] = reporter.groups.flatten()
        data["reporter"] = reporter
    
    return data

@register.inclusion_tag("reporters/partials/groups/index.html")
def groups_index():
    return { "groups": ReporterGroup.objects.flatten() }


@register.inclusion_tag("reporters/partials/groups/form.html")
def group_form(group=None):
    
    # fetch all groups, to be displayed
    # flat in the "parent group" field
    groups = ReporterGroup.objects.flatten()
    
    # if we are editing a group, iterate
    # the parents, and mark one of them
    # to pre-select it in the dropdown
    if group is not None:
        for grp in groups:
            if group.parent == grp:
                grp.selected = True
    
    return {
        "group": group,
        "groups": groups
    }


@register.inclusion_tag("reporters/partials/groups/widget.html")
def group_widget(group=None):
    
    groups = ReporterGroup.objects.flatten()
    if group is not None:
        for grp in groups:
            if grp == group.parent:
                grp.selected = True
    
    return {
        "groups": groups,
        "group": group
    }


@register.inclusion_tag("reporters/partials/connection/widget.html")
def connection_widget(connection=None):
    
    backends = PersistantBackend.objects.all()
    if connection is not None:
        for be in backends:
            if connection.backend == be:
                be.selected = True
    
    return {
        "backends": backends,
        "connection": connection
    }
