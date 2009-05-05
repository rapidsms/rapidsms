#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


from datetime import datetime, timedelta


from apps.reporters.models import *
from apps.supply.models import *
from apps.nigeria.models import *



@register.inclusion_tag("nigeria/partials/recent.html")
def recent_reporters(number=4):
    last_connections = PersistantConnection.objects.filter(reporter__isnull=False).order_by("-last_seen")[:number]
    last_reporters = [conn.reporter for conn in last_connections]
    return { "reporters": last_reporters }


@register.inclusion_tag("nigeria/partials/stats.html")
def nigeria_stats():
    return { "stats": [
#        {
#            "caption": "Callers",
#            "value":   PersistantConnection.objects.count()
#        },
        {
            "caption": "Reporters",
            "value":   Reporter.objects.count()
        },
        {
            "caption": "Active Locations",
            "value":   PartialTransaction.objects.values("destination").distinct().count() +
                       CardDistribution.objects.values("location").distinct().count()
        },
        {
            "caption": "Stock Transfers",
            "value":   PartialTransaction.objects.count()
        },
        {
            "caption": "Card Reports",
            "value":   CardDistribution.objects.count()
        },
        {
            "caption": "Coupons Distributed",
            "value":   sum(CardDistribution.objects.values_list("distributed", flat=True))
        },
#        {
#            "caption": "Coupon Recipients",
#            "value":   sum(CardDistribution.objects.values_list("people", flat=True))
#        }
    ]}


@register.inclusion_tag("nigeria/partials/progress.html")
def daily_progress():
    start = datetime(2009, 05, 04)
    end = datetime(2009, 05, 18)
    days = []
    
    
    # how high should we aim?
    report_target    = 100.0
    coupon_target    = 5000.0
    recipient_target = 50000.0
    
    
    for d in range(0, (end - start).days):
        date = start + timedelta(d)
        
        args = {
            "time__year":  date.year,
            "time__month": date.month,
            "time__day":   date.day
        }
        
        data = {
            "number": d+1,
            "date": date,
            "in_future": date > datetime.now()
        }
        
        if not data["in_future"]:
            data.update({
                "reports": CardDistribution.objects.filter(**args).count(),
                "coupons": sum(CardDistribution.objects.filter(**args).values_list("distributed", flat=True)),
                "recipients": sum(CardDistribution.objects.filter(**args).values_list("people", flat=True))
            })
        
            data.update({
                "reports_perc":    int((data["reports"]    / report_target)    * 100) if (data["reports"]    > 0) else 0,
                "coupons_perc":    int((data["coupons"]    / coupon_target)    * 100) if (data["coupons"]    > 0) else 0,
                "recipients_perc": int((data["recipients"] / recipient_target) * 100) if (data["recipients"] > 0) else 0,
            })
        
        days.append(data)
    
    return { "days": days }
