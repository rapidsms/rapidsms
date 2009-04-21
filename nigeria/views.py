#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction
from rapidsms.webui.utils import render_to_response
from django.db import models
from random import randrange, seed

import sys

locid = "20"
lgas = Location.objects.filter(code=locid)[0].children.all()[0:10]
stocklevel_perlocation_data = []
seed()

for lga in lgas:
    stocklevel_perlocation_data.extend({'label': lga.name, 'data': [[len(stocklevel_perlocation_data)+1, randrange(1000, 5000, 100)]]})

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
    

    return render_to_response(req, "nigeria/index.html",{})

def logistics_summary(req, locid):
    transactions = Transaction.objects.all().order_by("shipment__sent").reverse()
    return render_to_response(req, "nigeria/logistics_summary.html", {'transactions': transactions})

def supply_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/supply_summary.html")

def bednets_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/bednets_summary.html")

def coupons_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/coupons_summary.html")


# Periodical Reporting  by day, week, month for coupons
def coupons_daily(req, locid):
    location = False
    try:
        location_object = Location.objects.get(code=locid)
        location = {'name': location_object.name}
    except: pass
    return render_to_response(req, "nigeria/coupons_daily.html", {'location': location})

def coupons_weekly(req, locid):
    return render_to_response(req, "nigeria/coupons_weekly.html")

def coupons_monthly(req, locid):
    return render_to_response(req, "nigeria/coupons_monthly.html")


# Periodical Reporting  by day, week, month for bednets
def bednets_daily(req, locid):
    return render_to_response(req, "nigeria/bednets_daily.html")

def bednets_weekly(req, locid):
    return render_to_response(req, "nigeria/bednets_weekly.html")

def bednets_monthly(req, locid):
    return render_to_response(req, "nigeria/bednets_monthly.html")


# Periodical Reporting  by day, week, month for supply
#Builds daily supply reporting
def supply_daily(req, locid):
    return render_to_response(req, "nigeria/supply_daily.html")

#Builds weekly supply detail
def supply_weekly(req, locid):
    return render_to_response(req, "nigeria/supply_weekly.html")

#Build Monthly supply detail
def supply_monthly(req, locid):
    return render_to_response(req, "nigeria/supply_monthly.html")

#This portion of code is for testing
def tests(req):
    return render_to_response(req, "nigeria/testpages/trees.html")

