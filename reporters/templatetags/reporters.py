#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


import datetime
from django.utils.timesince import timesince
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import date as filter_date, time as filter_time




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




class SelfLinkFieldsNode(template.Node):
    def __init__(self, *args):
        self.omit = args
        
    def render(self, context):
        get = context["request"].GET
        
        # render ALL of the GET parameters,
        # except for those given in args
        return "".join([
            '<input type="hidden" name="%s" value="%s" />' % (k, get[k])
            for k in get.keys()
            if k not in self.omit
        ])

@register.tag
def self_link_fields(parser, token):
    args = token.split_contents()
    return SelfLinkFieldsNode(*args[1:])




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
