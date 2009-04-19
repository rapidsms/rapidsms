#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.shortcuts import get_object_or_404, render_to_response
from django.db import IntegrityError, transaction

from rapidsms.webui.utils import *
from apps.reporters.models import *
from apps.reporters.utils import *


def message(req, msg, link=None):
    return render_to_response(req,
        "message.html", {
            "message": msg,
            "link": link
    })




@require_GET
def index(req):
    return render_to_response(req,
        "reporters/reporters/index.html")


def update_reporter(req, rep):
    
    # as default, we will delete all of the connections
    # and groups from this reporter. the loops will drop
    # any objects that we should NOT DELETE
    del_conns = list(rep.connections.values_list("pk", flat=True))
    del_grps = list(rep.groups.values_list("pk", flat=True))


    # iterate each of the connection widgets from the form,
    # to make sure each of them are linked to the reporter
    connections = field_bundles(req.POST, "conn-backend", "conn-identity")
    for be_id, identity in connections:
        
        # create the new connection - this could still
        # raise a DoesNotExist (if the be_id is invalid),
        # or an IntegrityError or ValidationError (if the
        # identity or report is invalid)
        conn, created = PersistantConnection.objects.get_or_create(
            backend=PersistantBackend.objects.get(pk=be_id),
            identity=identity,
            reporter=rep)
        
        # if this conn was already
        # linked, don't delete it!
        if conn.pk in del_conns:
            del_conns.remove(conn.pk)


    # likewise for the group objects
    groups = field_bundles(req.POST, "group")	
    for grp_id, in groups:
        
        # link this group to the reporter
        grp = ReporterGroup.objects.get(pk=grp_id)
        rep.groups.add(grp)
        
        # if this group was already
        # linked, don't delete it!
        if grp.pk in del_grps:
            del_grps.remove(grp.pk)
    
    
    # delete all of the connections and groups 
    # which were NOT in the form we just received
    rep.connections.filter(pk__in=del_conns).delete()
    rep.groups.filter(pk__in=del_grps).delete()


@require_http_methods(["GET", "POST"])
def add_reporter(req):
    def get(req):
        return render_to_response(req,
            "reporters/reporters/add.html")

    @transaction.commit_manually
    def post(req):
        try:
            # create the reporter object from the form
            rep = insert_via_querydict(Reporter, req.POST)
            rep.save()
            
            # every was created, so really
            # save the changes to the db
            update_reporter(req, rep)
            transaction.commit()
            
            # full-page notification
            return message(req,
                "Reporter %d added" % (rep.pk),
                link="/reporters")
        
        except Exception, err:
            
            # roll back the transaction, to avoid creating
            # a reporter with no connections, if the error
            # came late in the creation process
            transaction.rollback()
            	
            # something went wrong during object creation.
            # this should have been caught by javascript,
            # so halt with a low-tech but safe error
            return HttpResponseServerError(
                "\n".join(list(e for e in err)),
                content_type="text/plain")
    
    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)


@require_http_methods(["GET", "POST"])  
def edit_reporter(req, pk):
    rep = get_object_or_404(Reporter, pk=pk)
    
    def get(req):
        return render_to_response(req,
            "reporters/reporters/edit.html", {
            "reporter": rep })
    
    @transaction.commit_manually
    def post(req):
        try:
            # automagically update the fields of the
            # reporter object, from the form
            update_via_querydict(rep, req.POST).save()
            update_reporter(req, rep)
            
            # no exceptions, so no problems
            # commit everything to the db
            transaction.commit()
            
            # full-page notification
            return message(req,
                "Reporter %d updated" % (rep.pk),
                link="/reporters")
        
        except Exception, err:
            transaction.rollback()
            return HttpResponseServerError(
                "\n".join(list(e for e in err)),
                content_type="text/plain")
        
    # invoke the correct function...
    # this should be abstracted away
    if   req.method == "GET":  return get(req)
    elif req.method == "POST": return post(req)




@require_GET
def index_groups(req):
    return render_to_response(req,
        "reporters/groups/index.html", {
            "groups": ReporterGroup.objects.flatten()
    })


@require_http_methods(["GET", "POST"])
def add_group(req):
    if req.method == "GET":
        return render_to_response(req,
            "reporters/groups/add.html", {
                "groups": ReporterGroup.objects.flatten() })
        
    elif req.method == "POST":
        grp = insert_via_querydict(ReporterGroup, req.POST)
        grp.save()
        
        return message(req,
            "Group %d added" % (grp.pk),
            link="/reporters/groups/")


@require_http_methods(["GET", "POST"])
def edit_group(req, pk):
    if req.method == "GET":
        return render_to_response(req,
            "reporters/groups/edit.html", {
                "group": get_object_or_404(ReporterGroup, pk=pk),
                "groups": ReporterGroup.objects.flatten() })
        
    elif req.method == "POST":
        grp = update_via_querydict(ReporterGroup, req.POST)
        grp.save()
        
        return message(req,
            "Group %d saved" % (grp.pk),
            link="/reporters/groups/")
