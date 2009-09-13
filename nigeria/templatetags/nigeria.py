#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


from datetime import datetime, timedelta


from reporters.models import *
from supply.models import *
from nigeria.models import *



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

    # Dawakin Kudu      99,379
    # Garum Mallam      51,365
    # Kano Municipal    161,168
    # Kura              63,758
    coupon_target    = 375670.0

    # Dawakin Kudu      248,447
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
    
    total_netcards = sum(CardDistribution.objects.all().values_list("distributed", flat=True))
    netcards_stats = int(float(total_netcards) / coupon_target * 100) if (total_netcards > 0) else 0

    total_beneficiaries = sum(CardDistribution.objects.all().values_list("people", flat=True))
    beneficiaries_stats = int(float(total_beneficiaries) / recipient_target * 100) if (total_beneficiaries > 0) else 0

    return { "days": days, 
            "netcards_stats": netcards_stats, 
            "beneficiaries_stats": beneficiaries_stats,
            "total_netcards": total_netcards,
            "total_beneficiaries": total_beneficiaries}


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
        style = "" 
        if reports.count() == 0:
            style = "warning" 

        return {
            "name":          ward.name,
            "contact":       ward.one_contact('WS', True),
            "reports":       reports.count(),
            "netcards":      sum(reports.values_list("distributed", flat=True)),
            "beneficiaries": sum(reports.values_list("people", flat=True)),
            "class":         style}
    
    # called to fetch and assemble the
    # data structure for each pilot LGA
    def __lga_data(lga):
        projections = {
            "netcards" : {
                        "DAWAKIN KUDU"   : 99379.0,
                        "GARUN MALLAM"   : 51365.0,
                        "KANO MUNICIPAL" : 161168.0,
                        "KURA"           : 63758.0 },
            "beneficiaries" : {
                        "DAWAKIN KUDU"   : 248447.0,
                        "GARUN MALLAM"   : 128412.0,
                        "KANO MUNICIPAL" : 402919.0,
                        "KURA"           : 159394.0 },
        }

        wards = lga.children.all()
        reporters = Reporter.objects.filter(location__in=wards)
        supervisors = reporters.filter(role__code__iexact="WS")
        summary = "%d supervisors in %d wards" % (supervisors.count(), wards.count())
        
        ward_data = map(__ward_data, wards)
        def __wards_total(key):
            return sum(map(lambda w: w[key], ward_data))
        
        def __stats(key):
            return int(float(__wards_total(key)) / projections[key][str(lga.name)] * 100) if (__wards_total(key) > 0) else 0 

        return {
            "name":                     lga.name,
            "summary":                  summary,
            "netcards_projected":       int(projections['netcards'][str(lga.name)]),
            "netcards_total":           int(__wards_total("netcards")),
            "beneficiaries_projected":  int(projections['beneficiaries'][str(lga.name)]),
            "beneficiaries_total":      int(__wards_total("beneficiaries")),
            "wards":                    ward_data,
            "reports":                  __wards_total("reports"),
            "netcards":                 __wards_total("netcards"),
            "beneficiaries":            __wards_total("beneficiaries"),
            "netcards_stats":           __stats("netcards"),
            "beneficiaries_stats":      __stats("beneficiaries")
        }

    return { "pilot_lgas": map(__lga_data, lgas) }


@register.inclusion_tag("nigeria/partials/logistics.html")
def logistics_summary():

    # called to fetch and assemble the data structure
    # for each LGA, containing the flow of stock
    def __lga_data(lga):
        incoming = PartialTransaction.objects.filter(destination=lga, type__in=["R", "I"]).order_by("-date")
        outgoing = PartialTransaction.objects.filter(origin=lga, type__in=["R", "I"]).order_by("-date")
        return {
            "name":         unicode(lga),
            "transactions": incoming | outgoing, 
            "logistician": lga.one_contact('SM', True)}
    
    # process and return data for ALL LGAs for this report
    return { "lgas": map(__lga_data, LocationType.objects.get(name="LGA").locations.all()) }

@register.inclusion_tag("nigeria/partials/mobilization_summary_charts.html")
def mobilization_summary_charts():
    summary = pilot_summary()
    netcards_projected = []
    netcards_total = []
    beneficiaries_projected = []
    beneficiaries_total = []
    lga_names = []

    pilot_lgas = summary['pilot_lgas']
    for lga in pilot_lgas:
        netcards_projected.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 1, lga['netcards_projected']))
        netcards_total.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 2, lga['netcards_total']))
        beneficiaries_projected.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 1, lga['beneficiaries_projected']))
        beneficiaries_total.append("[%d, %d]" % (pilot_lgas.index(lga) * 3 + 2, lga['beneficiaries_total']))
        lga_names.append("[%d, '%s']" % (pilot_lgas.index(lga) * 3 + 2, lga['name']))
    return {
        "beneficiaries_projected": "[%s]" % ",".join(beneficiaries_projected),
        "beneficiaries_total": "[%s]" % ",".join(beneficiaries_total),
        "netcards_projected": "[%s]" % ",".join(netcards_projected),
        "netcards_total": "[%s]" % ",".join(netcards_total),
        "lgas": "[%s]" % ",".join(lga_names)
    }
