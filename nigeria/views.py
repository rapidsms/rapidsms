#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from django.shortcuts import render_to_response
from django.db import models

import sys

#Views for handling summary of Reports Displayed as Location Tree
def index(req):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    states = Location.objects.all().filter(type__name="State")

    for state in states:
        lgas = Location.objects.all().filter(type__name="LGA", code__startswith=state.code)
        states_dict={}
        lgas_dict={}
        wards_dict={}
        dps_dict={}
        mts_dict={}
    
        for lga in lgas:
            wards = Location.objects.all().filter(type__name="Ward", code__startswith=lga.code)
            lgas_dict[str(lga.name)]=str(lga.name)
            for ward in wards:
                dps =  Location.objects.all().filter(type__name="Distribution Point", code__startswith=ward.code)
                wards_dict[str(ward.name)] = str(ward.name)

                for dp in dps:
                    mts =  Location.objects.all().filter(type__name="Mobilization Team", code__startswith=dp.code)
                    dps_dict[str(dp.name)] = str(dp.name)
                    for mt in mts:
                        mts_dict[str(mt.name)]=str(mt.name)

                    dps_dict[dp.name]=mts_dict
                wards_dict[ward.name]=dps_dict
            lgas_dict[lga.name]=wards_dict
        states_dict[state.name]=lgas_dict
    

    return render_to_response("nigeria/index.html",{}, context_instance=RequestContext(req))


def supply_summary(req, frm, to, range):
    return render_to_response("nigeria/supply_summary.html", context_instance=RequestContext(req))

def bednets_summary(req, frm, to, range):
    return render_to_response("nigeria/bednets_summary.html", context_instance=RequestContext(req))

def coupons_summary(req, frm, to, range):
    return render_to_response("nigeria/coupons_summary.html", context_instance=RequestContext(req))


# Periodical Reporting  by day, week, month for coupons
def coupons_daily(req, locid):
    return render_to_response("nigeria/coupons_daily.html", context_instance=RequestContext(req))

def coupons_weekly(req, locid):
    return render_to_response("nigeria/coupons_weekly.html", context_instance=RequestContext(req))

def coupons_monthly(req, locid):
    return render_to_response("nigeria/coupons_monthly.html", context_instance=RequestContext(req))


# Periodical Reporting  by day, week, month for bednets
def bednets_daily(req, locid):
    return render_to_response("nigeria/bednets_daily.html", context_instance=RequestContext(req))

def bednets_weekly(req, locid):
    return render_to_response("nigeria/bednets_weekly.html", context_instance=RequestContext(req))

def bednets_monthly(req, locid):
    return render_to_response("nigeria/bednets_monthly.html", context_instance=RequestContext(req))


# Periodical Reporting  by day, week, month for supply
#Builds daily supply reporting
def supply_daily(req, locid):
    return render_to_response("nigeria/supply_daily.html", context_instance=RequestContext(req))

#Builds weekly supply detail
def supply_weekly(req, locid):
    return render_to_response("nigeria/supply_weekly.html", context_instance=RequestContext(req))

#Build Monthly supply detail
def supply_monthly(req, locid):
    return render_to_response("nigeria/supply_monthly.html", context_instance=RequestContext(req))

#This portion of code is for testing
def tests(req):
    return render_to_response("nigeria/testpages/trees.html", context_instance=RequestContext(req))

