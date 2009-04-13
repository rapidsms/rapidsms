#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404, render_to_response
from django.db import IntegrityError, transaction

from apps.reporters.models import *
from apps.reporters.utils import *


@require_GET
def index(req):
	return render_to_response("reporters/index.html",
	    {
	        "reporters": Reporter.objects.all(),
	        "backends": PersistantBackend.objects.all()
	    }, context_instance=RequestContext(req))


@require_POST
@transaction.commit_manually
def add_reporter(req):
    try:
        # create the reporter object from the form
        rep = insert_via_querydict(Reporter, req.POST)
        rep.save()
        
        # create each of the connection objects,
        # linked to the new reporter, from the form
        bundles = field_bundles(req.POST, "backend", "identity")
        for be_id, identity in bundles:
            
            # create the new connection - this could still
            # raise a DoesNotExist (if the be_id is invalid),
            # or an IntegrityError or ValidationError (if the
            # identity or report is invalid)
            PersistantConnection(
                backend=PersistantBackend.objects.get(pk=be_id),
                identity=identity,
                reporter=rep
            ).save()
        
        # every was created, so really
        # save the changes to the db
        transaction.commit()
        
        return HttpResponse(
            "Reporter %d added" % (rep.pk),
            content_type="text/plain")


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
