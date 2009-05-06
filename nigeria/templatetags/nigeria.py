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
    report_target    = 432.0 # 48 wards * 9 mobilization teams?
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
            "name":         ward.name,
            "reports":      reports.count(),
            "netcards":     sum(reports.values_list("distributed", flat=True)),
            "beneficiaries": sum(reports.values_list("people", flat=True))
        }
    
    # called to fetch and assemble the
    # data structure for each pilot LGA
    def __lga_data(lga):
        wards = lga.children.all()
        reporters = Reporter.objects.filter(location__in=wards)
        supervisors = reporters.filter(role__code__iexact="WS")
        
        summary = "%d supervisors (of %d reporters) in %d wards" % (len(supervisors), len(reporters), len(wards))
        
        return {
            "name": lga.name,
            "summary": summary,
            "wards": map(__ward_data, wards)
        }
    
    return { "pilot_lgas": map(__lga_data, lgas) }


def pilot_summaryx():
    pilot_lga_names = ['DAWAKIN KUDU', 'GARUN MALLAM', 'KURA', 'KANO MUNICIPAL']
    pilots = []
    for lga_name in pilot_lga_names:
        lga = Location.objects.get(name__iexact=lga_name, type__name='LGA')
        wards = Location.objects.filter(parent__pk=lga.pk)
        ws = Reporter.objects.filter(location__parent__pk=lga.pk).filter(role__code__iexact='ws')

        lga_data = { lga.name : [str(ws.count()) + " ward supervisors registered for " + str(wards.count()) + " wards",]}
        lga_wards = []
        reports = CardDistribution.objects.all()
        for ward in wards:
            # TODO move this functionality onto the model
            team_rep = reports.filter(location__parent__parent__pk=ward.pk)
            point_rep = reports.filter(location__parent__pk=ward.pk)
            ward_rep = reports.filter(location__pk=ward.pk)
            ward_reports = ward_rep.count() + point_rep.count() + team_rep.count()

            ward_cards = sum(ward_rep.values_list("distributed", flat=True))
            team_cards = sum(team_rep.values_list("distributed", flat=True))
            point_cards = sum(point_rep.values_list("distributed", flat=True))
            total_cards = ward_cards + team_cards + point_cards

            ward_data = {ward.name: [str(ward_reports) + " reports", str(total_cards) + " net cards distributed"]}
            lga_wards.append(ward_data)
        pilots.append([lga_data, lga_wards])
    return {"pilots" : pilots}


@register.inclusion_tag("nigeria/partials/logistics.html")
def logistics_summary():
    lgas = Location.objects.filter(type__name='LGA')
    partials = PartialTransaction.objects.exclude(status="A") 
    summaries = []
    for lga in lgas:
        lga_data = []
        lga_data.append(["name",  str(lga)])

        lga_receipts = partials.filter(destination=lga).filter(type="R")
        lga_data.append(["receipts", lga_receipts])

        lga_issues = partials.filter(origin=lga).filter(type="I")
        lga_data.append(["issues", lga_issues])
        summaries.append(dict(lga_data))
    return {"summaries" : summaries}
