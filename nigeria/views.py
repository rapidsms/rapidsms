#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction, Stock, PartialTransaction
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
from random import randrange, seed
import time
import sys

locid = "20"
lgas = Location.objects.filter(code=locid)[0].children.all()[0:10]
stocklevel_perlocation_data = []

for lga in lgas:
    stocklevel_perlocation_data.extend({'label': lga.name, 'data': [[len(stocklevel_perlocation_data)+1, randrange(1000, 5000, 100)]]})

#Views for handling summary of Reports Displayed as Location Tree
def index(req):
    
    lga_dict={}

    reload(sys)
    sys.setdefaultencoding('utf-8')
#Line below will be replaced by a for loop to iterate through objects for state retrieval
    state = Location.objects.get(code="20")
   
    lgas = state.children.all()[0:9]

    for lga in lgas:
        wards = lga.children.all()
   #     lga_dict2[lga] = wards
	lga_dict[lga] = wards

    states = ['Abia','Adamawa','Akwa-Ibom','Anambra','Bauchi','Bayelsa',
        'Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','FCT','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara']
    
    
# Logic below handles objects retrieval from Location Models

    return render_to_response(req, "nigeria/index.html",{'states':states, 'lgas':lga_dict})

def logistics_summary(req, locid):
    # Get the location we are going to work with.
    # If there is no location set, this will default to the first
    # one in the database.  If there are no locations in the
    # database we are SOL
    if not locid:
        locid = 1
    try: 
        location = Location.objects.get(pk=locid)
        _set_stock(location)
    except Location.DoesNotExist:
        location = None

    # get all the transactions that this location was involved in 
    transactions_from_loc = Transaction.objects.all().filter(shipment__origin=location) 
    transactions_to_loc = Transaction.objects.all().filter(shipment__destination=location)  
    transactions = (transactions_from_loc | transactions_to_loc).order_by("shipment__sent").reverse() 
        
    # get any place this location has shipped to or from.  
    # we will use these to generate some plots
    # and pass them forward to the template
    locations_shipped_to = []
    [locations_shipped_to.append(trans.shipment.destination) for trans in transactions_from_loc if trans.shipment.destination not in locations_shipped_to]
    
    # set the stock value in all the children.
    [_set_stock(child) for child in locations_shipped_to]
    
    # get some JSON strings for the plots
    stock_per_loc_data, stock_per_loc_options = _get_stock_per_location_strings(locations_shipped_to)
    stock_over_time_data, stock_over_time_options = _get_stock_over_time_strings([location])
    stock_over_time_child_data, stock_over_time_child_options = _get_stock_over_time_strings(locations_shipped_to)
    
    # send the whole list of stuff back to the template
    return render_to_response(req, "nigeria/logistics_summary.html", 
                              {'location': location,
                               'child_locations': locations_shipped_to,
                               'transactions': transactions,
                               'stock_per_loc_plot_data' : stock_per_loc_data, 
                               'stock_per_loc_plot_options' : stock_per_loc_options, 
                               'stock_over_time_data' : stock_over_time_data, 
                               'stock_over_time_options' : stock_over_time_options, 
                               'stock_over_time_child_data' : stock_over_time_child_data, 
                               'stock_over_time_child_options' : stock_over_time_child_options 
                               })

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




def _set_stock(location):
    '''Get the stock object associated with this.  None if none found'''
    try:
        location.stock = Stock.objects.get(location=location)
    except Stock.DoesNotExist:
        # this isn't a real error, we just don't have any stock information
        location.stock = None

        
def _get_stock_per_location_strings(locations):
    '''Get a JSON formatted list that flot can plot
       based on the data in the stock table'''
    # this is the sample format
    #data = '''[
    #        {"bars":{"show":true},"label":"Ajingi","data":[[-0.5,100]]},
    #        {"bars":{"show":true},"label":"Bebeji","data":[[0.5,650]]}
    #        ]'''
    
    # loop over all the locations and if they have a stock
    # create a string describing it and add it to the list.
    # count will store the index of each item.  
    count = 0
    rows = []
    for location in locations:
        # if the location doesn't have any stock we won't display it
        if location.stock:
            row = '{"bars":{"show":true},"label":"%s","data":[[%s,%s]]}' % (location.name, count, location.stock.balance)
            rows.append(row)
            count = count + 1
    data = "[%s]" % ", ".join(rows)
    options = '{"grid":{"clickable":true},"xaxis":{"min":0,"ticks":[],"tickFormatter":"string"},"yaxis":{"min":0}}'
    return (data, options)


def _get_stock_over_time_strings(locations):
    '''Get a JSON formatted list that flot can plot
       based on the data in the stock table'''
    
    # this is the sample format
    #data = '''[
    #        {"label":"Ajingi","data":[[1239706800000,1000],[1239793200000,800],[1239966000000,650]]},
    #        {"label":"Bebeji","data":[[1239706800000,500],[1239793200000,350],[1239836400000,250]]},
    #        ]'''
    
    rows = []
    for location in locations:
        # get all the partial transactions that affected this stock
        updates = PartialTransaction.get_all_with_stock_updates(location).order_by("date")
        if len(updates) > 0:
            update_strings = []
            for update in updates:
                ud_time = str(time.mktime(update.date.timetuple()))
                udt_formatted = ud_time[0:ud_time.find(".")] + "000"
                update_strings.append("[%s,%s]" % (udt_formatted, update.stock))
            #print "adding update for %s" % location 
            rows.append('{"label":"%s", "data":[%s]}' % (location.name, ",".join(update_strings)))
    data = "[%s]" % (",".join(rows))
    #data_for_dates = [label":"KANO", "data":[[1240316478.0,1800]]}];\n                    
    # todo: make this real
    #data = '[{"label":"Ajingi","data":[[1239706800000,1000],[1239793200000,800],[1239836400000,700],[1239966000000,650],[1240052400000,450],[1240138800000,350],[1240182000000,200],[1240268400000,100]]},{"label":"Bebeji","data":[[1239706800000,500],[1239793200000,350],[1239836400000,250],[1239966000000,1250],[1240052400000,1000],[1240138800000,900],[1240182000000,700],[1240268400000,650]]},{"label":"Bichi","data":[[1239706800000,1500],[1239793200000,1500],[1239836400000,1500],[1239966000000,1200],[1240052400000,1100],[1240138800000,1000],[1240182000000,850],[1240268400000,750]]},{"label":"Dala","data":[[1239706800000,200],[1239793200000,1500],[1239836400000,1250],[1239966000000,1100],[1240052400000,900],[1240138800000,600],[1240182000000,300],[1240268400000,100]]},{"label":"Garko","data":[[1239706800000,750],[1239793200000,450],[1239836400000,250],[1239966000000,250],[1240052400000,250],[1240138800000,50],[1240182000000,750],[1240268400000,500]]}];'
    options = '{"bars":{"show":false},"points":{"show":true},"grid":{"clickable":false},"xaxis":{"mode":"time","timeformat":"%m/%d/%y"},"yaxis":{"min":0},"legend":{"show":true},"lines":{"show":true}}'
    return (data, options)
