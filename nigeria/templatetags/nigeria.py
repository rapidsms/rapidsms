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
            "caption": "Net Card Reports",
            "value":   CardDistribution.objects.count()
        },
        {
            "caption": "Net Cards Distributed",
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
    # 48 wards * 9 mobilization teams = 482?
    # but at least 2 lgas are summing teams
    # and reporting once by ward, so maybe 48 * 4?
    report_target    = 192.0

    # Dawakin Kudo      99,379
    # Garum Mallam      51,365
    # Kano Municipal    161,168
    # Kura              63,758
    coupon_target    = 375670.0

    # Dawakin Kudo      248,447
    # Garun Mallam      128,412
    # Kano Municipal    402,919
    # Kura              159,394
    recipient_target = 939172.0
    
    
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
                "recipients_perc":    int((data["recipients"]    / recipient_target)    * 100) if (data["recipients"]    > 0) else 0,
            })
        
        days.append(data)
    
    return { "days": days }


@register.inclusion_tag("nigeria/partials/pilot.html")
def pilot_summary():
    
    # fetch all of the LGAs that we want to display
    lga_names = ["DAWAKIN KUDU", "GARUN MALLAM", "KURA", "KANO MUNICIPAL"]
    lgas = LocationType.objects.get(name="LGA").locations.filter(name__in=lga_names)
    
    # called to fetch and assemble the
    # data structure for each pilot ward
    def __ward_data(ward):
        locations = ward.descendants(True)
        reports = CardDistribution.objects.filter(location__in=locations)
        
        return {
            "name":          ward.name,
            "reports":       reports.count(),
            "netcards":      sum(reports.values_list("distributed", flat=True)),
            "beneficiaries": sum(reports.values_list("people", flat=True)) }
    
    # called to fetch and assemble the
    # data structure for each pilot LGA
    def __lga_data(lga):
        wards = lga.children.all()
        reporters = Reporter.objects.filter(location__in=wards)
        supervisors = reporters.filter(role__code__iexact="WS")
        summary = "%d supervisors in %d wards" % (len(supervisors), len(wards))
        
        ward_data = map(__ward_data, wards)
        def __wards_total(key):
            return sum(map(lambda w: w[key], ward_data))
        
        return {
            "name":          lga.name,
            "summary":       summary,
            "wards":         ward_data,
            "reports":       __wards_total("reports"),
            "netcards":      __wards_total("netcards"),
            "beneficiaries": __wards_total("beneficiaries") }
    
    return { "pilot_lgas": map(__lga_data, lgas) }


@register.inclusion_tag("nigeria/partials/logistics.html")
def logistics_summary():

    # called to fetch and assemble the data structure
    # for each LGA, containing the flow of stock
    def __lga_data(lga):
        return {
            "name":         unicode(lga),
            "transactions": PartialTransaction.objects.filter(destination=lga, type__in=["R", "I"]).order_by("-date") }
    
    # process and return data for ALL LGAs for this report
    return { "lgas": map(__lga_data, LocationType.objects.get(name="LGA").locations.all()) }
