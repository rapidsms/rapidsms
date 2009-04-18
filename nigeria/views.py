#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from django.shortcuts import render_to_response
import sys

#Views for handling summary of Reports Displayed as Location Tree
def index(req):
    
    reload(sys)
    sys.setdefaultencoding('utf-8')
    states = Location.objects.all().filter(type__name="State")
    
    for state in states:
       # print "%s: %s" % (state.name, state.code)
        lgas = Location.objects.all().filter(type__name="LGA", code__startswith=state.code)
        dictn={'lgas':lgas}   
         #for lga in lgas:
            #print "---%-15s: %6s" % (lga.name, lga.code)

            #wards = Location.objects.all().filter(type__name="Ward", code__startswith=lga.code)
            #for ward in wards:
                #print "------%-15s: %8s" % (str(ward.name), ward.code)

    return render_to_response("nigeria/index.html",dictn, context_instance=RequestContext(req))


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

