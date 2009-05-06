#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, Http404
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction, Stock, PartialTransaction
from apps.nigeria.models import CardDistribution
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
from django.core.paginator import *
from random import randrange, seed
from contrib.flotgrapher.grapher import FlotGraph

import time
import sys

#Parameter for paging reports outputs
ITEMS_PER_PAGE = 20

#This is required for ***unicode*** characters***
# do we really need to reload it?  TIM to check
reload(sys)
sys.setdefaultencoding('utf-8')

#Views for handling summary of Reports Displayed as Location Tree
def index(req, locid=None):
    if not locid:
        locid = 1
    try:
        location = Location.objects.get(id=locid)
    except Location.DoesNotExist:
        location= None
    #print "location: %s" % location
    return render_to_response(req, "nigeria/index.html",{'location':location })


def logistics_summary(req, locid):
    # Get the location we are going to work with.
    # If there is no location set, this will default to the first
    # one in the database.  If there are no locations in the
    # database we are S.O.L.
    if not locid:
        locid = 1
    try: 
        location = Location.objects.get(pk=locid)
    except Location.DoesNotExist:
        location = None

    # get all the partialtransactions that this location is involved in 
    transactions_from_loc = PartialTransaction.objects.all().filter(origin=location) 
    transactions_to_loc = PartialTransaction.objects.all().filter(destination=location)  
    transactions = (transactions_from_loc | transactions_to_loc).order_by("-date") 
        
    # get any place this location has shipped to or from.  
    # we will use these to generate some plots
    # and pass them forward to the template
    locations_shipped_to = []
    [locations_shipped_to.append(trans.destination) for trans in transactions_from_loc if trans.destination not in locations_shipped_to]
    
    # set the stock value in all the children.
    # this is now handled by signals!  see supply/models.py
    #[_set_stock(child) for child in locations_shipped_to]
    
    # get some JSON strings for the plots
    stock_per_loc_data, stock_per_loc_options = _get_stock_per_location_strings(locations_shipped_to)
    stock_over_time_data, stock_over_time_options = _get_stock_over_time_strings([location])
    stock_over_time_child_data, stock_over_time_child_options = _get_stock_over_time_strings(locations_shipped_to)
    
    paginator = Paginator(transactions, ITEMS_PER_PAGE)

    try:
        page = int(req.GET['page'])
    except:
        page = 1

    try:
        transactions_pager = paginator.page(page)
    except:
        raise Http404

    # send the whole list of stuff back to the template
    return render_to_response(req, "nigeria/logistics_summary.html", 
                              {'location': location,
                               'child_locations': locations_shipped_to,
                               'transactions_pager': transactions_pager,
                               'paginator': paginator,
                               'page': page,
                               'stock_per_loc_plot_data' : stock_per_loc_data, 
                               'stock_per_loc_plot_options' : stock_per_loc_options, 
                               'stock_over_time_data' : stock_over_time_data, 
                               'stock_over_time_options' : stock_over_time_options, 
                               'stock_over_time_child_data' : stock_over_time_child_data, 
                               'stock_over_time_child_options' : stock_over_time_child_options 
                               })

def generate(req):
    # for the demo, to quickly generate dps and teams for all wards
    all_wards = Location.objects.all().filter(type__name__iexact="ward")
    dps_per_ward = 3
    teams_per_dp = 4
    dp_type = LocationType.objects.get(name__iexact="Distribution Point")
    team_type = LocationType.objects.get(name__iexact="Mobilization Team")
    teams_created = 0
    dps_created = 0
    ward_count = 1
    for ward in all_wards:
        print "ward: %s, %s of %s" %(ward.name, ward_count, len(all_wards))
        ward_count = ward_count + 1
        # assume if this ward already has DPs we don't need to do this
        if (len(ward.children.all()) > 0):
            continue
        for dp_id in range(1, dps_per_ward + 1):
            dp_name = "%s DP %s" %(ward.name, dp_id)
            dp_code = "%s%s" % (ward.code, dp_id)
            dp = Location.objects.create(name=dp_name, type=dp_type, code=dp_code, parent=ward)
            dps_created = dps_created + 1
            for team_id in range(1, teams_per_dp + 1):
                team_name = "%s TEAM %s" %(dp_name, team_id)
                team_code = "%s%s" % (dp_code, team_id)
                team = Location.objects.create(name=team_name, type=team_type, code=team_code, parent=dp)
                teams_created = teams_created + 1
    return HttpResponse("Successfully created %s distribution points and %s teams" % (dps_created, teams_created))
    
def supply_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/supply_summary.html")

def bednets_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/bednets_summary.html")

def coupons_summary(req, locid=1):
    #Declarations
    coupons_distribution_data_per_ward = []
    coupons_distribution_data_over_time = []  
    try: 
        location = Location.objects.get(pk=locid)
        parent = location.parent
        location_type = Location.objects.get(pk=locid).type
        loc_children = []
        bar_data = []
        pie_data = {"settlements" : [], "people" : [], "coupons": []}
        index = 0
        # The loop below will be replaced by a neater code when method of returning children field properties are discovered
        coupon_data = []
        people_data = []
        settlements_data = []
        labels = []
        type = ""
        for child in location.children.all():
            people, coupons, settlements = _get_card_distribution_data(child)
            child.people = people
            child.settlements = settlements
            child.coupons = coupons
            type = child.type
            if child.people or child.settlements or child.coupons:
                settlements_data.append([index, child.settlements])
                people_data.append([index + 1, child.people])
                coupon_data.append([index + 2, child.coupons])
                # you need to add the str() to prevent the leading unicode 
                # character from showing up, which blows up flot
                labels.append(str(child.name))
                #bar_data.append({'data' : [[index, coupons]], "bars":{"show":"true"}, "label":str(child.name)})
                pie_data["coupons"].append({ "label": str(child.name),  "data": child.coupons})
                pie_data["settlements"].append({ "label": str(child.name),  "data": child.settlements})
                pie_data["people"].append({ "label": str(child.name),  "data": child.people})
                index += 4
            loc_children.append(child)
    except Location.DoesNotExist:
        location = None
    
    bar_data.append({"data" : settlements_data, "bars": { "show" : "true" }, "label":"settlements"})
    bar_data.append({"data" : people_data, "bars": { "show" : "true" }, "label":"people"})
    bar_data.append({"data" : coupon_data, "bars": { "show" : "true" }, "label":"coupons"})
    
    ticks = [[index * 4 + 1.5, label] for index, label in enumerate(labels)]
    
    return render_to_response(req, "nigeria/coupons_summary.html", {'location': location,
                     'children' : loc_children, 
                     'child_type':type, 
                     'parent':parent, 
                     'bar_data':bar_data,
                     'bar_ticks':ticks,
                     'pie_data': pie_data
                     }
                 )
    
#    new_graph = FlotGraph()
#    new_graph.set_data(bar_data)
#    test_flot = new_graph.generate_javascript()
#    return render_to_response(req, "nigeria/flot_test.html", {
#                     'test_flot':    test_flot
#                     }
#                 )





# Periodical Reporting  by day, week, month for coupons
def coupons_daily(req, locid=1):
    #Declarations
    coupons_distribution_data_per_ward = []
    coupons_distribution_data_over_time = []  
    child = Location.objects.get(pk=locid).children.all()[0]
    try: 
        location = Location.objects.get(pk=locid)
        location_type = Location.objects.get(pk=locid).type
        loc_children = []
        bar_data = []
        pie_data = []
        index = 0
        # The loop below will be replaced by a neater code when method of returning children field properties are discovered
        for child in location.children.all():
            people, coupons, settlements = _get_card_distribution_data(child)
            child.people = people
            child.settlements = settlements
            child.coupons = coupons
            type = child.type
            if coupons != 0:
                # you need to add the str() to prevent the leading unicode 
                # character from showing up, which blows up flot
                bar_data.append({'data' : [[index, coupons]], "bars":{"show":"true"}, "label":str(child.name)})
                pie_data.append({ "label": str(child.name),  "data": child.coupons})
                index += 1
            else:
                #hack
                child.coupons = 100
            loc_children.append(child)
    except Location.DoesNotExist:
        location = None

    #TODO: Generate and Send all plots data from here to the templates
    

    coupons_data_for_dps_mts1 = [[1,100],[5,60],[9,70],[13,40]]
    coupons_data_for_dps_mts2 = [[2,50],[6,60],[10,60],[14,100]]
    coupons_data_for_dps_mts3 = [[3,50],[7,60],[11,60],[15,100]]

    overflow_data = [[20,0]]
    bar_options = '{"xaxis":{"min":0,"ticks":[],"tickFormatter":"string"},"yaxis":{"min":0}}'
    coupons_data =  [{ 'data': coupons_data_for_dps_mts1, "bars": { "show": "true"}, "label":"MT 1" },
                     {'data': coupons_data_for_dps_mts2, "bars": { "show": "true" },"label":"MT 2" },
                     { 'data': coupons_data_for_dps_mts3, "bars": { "show": "true" },"label":"MT 3" },
                     { 'data': overflow_data, "bars": { "show": "true", "fill": "true", "fillColor":"#FFFFFF","label":"MT 4" }} ] 
    return render_to_response(req, "nigeria/coupons_daily.html", {'location': location,
                     'children' : loc_children, 
                     'type':type, 
                     'child':child, 
                     'coupons_data':coupons_data,
                     'bar_data':bar_data,
                     'bar_options':bar_options,
                     'pie_data': pie_data
                     }
                 )
    
    

def coupons_weekly(req, locid):
    return render_to_response(req, "nigeria/coupons_weekly.html")

def coupons_monthly(req, locid):
    return render_to_response(req, "nigeria/coupons_monthly.html")


# Periodical Reporting  by day, week, month for bednets
def bednets_daily(req, locid):
    if not locid:
        locid = 1
    try: 
        location = Location.objects.get(pk=locid)
        #_set_stock(location)
    except Location.DoesNotExist:
        location = None
        
    return render_to_response(req, "nigeria/bednets_daily.html", {'location': location})

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

def _get_distribution_over_time_strings(ward):
    '''Get a JSON formated list for flot plots on the template, 
    based on data in the Nets Distribution Data'''
    
def _get_distribution_per_distribution_team_strings(location):
    '''Get a JSON formated list for flot plots on the template, 
    based on data in the Nets Distribution Data'''
    
def _get_mobilization_data_over_time_strings(ward):
    '''Get a JSON formated list for flot plots on the template, 
    based on data in the Net Cards Distribution Data'''
    
    
def _get_mobilization_data_per_mobilization_team_string(ward):
    '''Get a JSON formated list for flot plots on the template, 
    based on data in the Net Cards Distribution Data'''

def _get_card_distribution_data(location):
    people = location.card_data["people"]
    coupons = location.card_data["distributed"]
    settlements = location.card_data["settlements"]
    for child in location.children.all():
        child_data = _get_card_distribution_data(child)
        people += child_data[0]
        coupons += child_data[1]
        settlements += child_data[2]
    return int(people), int(coupons), int(settlements)
 
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
    options = '{"bars":{"show":false},"points":{"show":true},"grid":{"clickable":false},"xaxis":{"mode":"time","timeformat":"%m/%d/%y"},"yaxis":{"min":0},"legend":{"show":true},"lines":{"show":true}}'    
    return (data, options)
