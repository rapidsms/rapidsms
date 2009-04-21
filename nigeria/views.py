#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
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
    wards_list = []
    ward_objects = {}
    lga_dict={}
    lga_code_dict={}
    codes = {}
    wards_code_list = []


    reload(sys)
    sys.setdefaultencoding('utf-8')
#Line below will be replaced by a for loop to iterate through objects for state retrieval
    state = Location.objects.get(code="20")
    
    lga_objects = state.children.all()[0:8]
    
    for i in range(8):
        lga_dict[str(lga_objects[i].name)] = {}
        wards_objects = lga_objects[i].children.all()[0:5]
        
        wards_list = []
        wards_code_list = []
        for n in range(wards_objects.count()):
    #        wards_dict[str(wards_objects[n].name)] = str(wards_objects[n].name)
            wards_list.append(str(wards_objects[n].name))
            wards_code_list.append(str(wards_objects[n].code))
        lga_dict[str(lga_objects[i].name)] = wards_list
        codes[str(lga_objects[i].code)] = wards_code_list
        

    states = ['Abia','Adamawa','Akwa-Ibom','Anambra','Bauchi','Bayelsa',
        'Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','FCT','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara']
    
    
# Logic below handles objects retrieval from Location Models

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


