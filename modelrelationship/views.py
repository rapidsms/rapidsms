# Create your views here.
from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.exceptions import *
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.utils.translation import ugettext_lazy as _
from django.db.models.query_utils import Q
from django.core.urlresolvers import reverse

from datetime import timedelta
from django.db import transaction


from modelrelationship.models import *
from modelrelationship.forms import *
from django.contrib.auth.models import User 
from django.contrib.contenttypes.models import ContentType

#from forms import *
import logging
import hashlib
import settings
import traceback
import sys
import os
import string


def all_types(request, template_name="modelrelationship/all_types.html"):
    context = {}
    edgetypes = ContentType.objects.all()
    context['content_types'] = edgetypes    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def single_contenttype(request, contenttype_id, template_name="modelrelationship/single_contenttype.html"):
    context = {}
    ctype = ContentType.objects.all().get(id=contenttype_id)
    context['content_type'] = ctype
    context['edgetypes_parent'] = EdgeType.objects.all().filter(parent_type=ctype)
    context['edgetypes_child'] = EdgeType.objects.all().filter(child_type=ctype)    
    context['instances'] = ctype.model_class().objects.all()
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def all_edgetypes(request, template_name="modelrelationship/all_edgetypes.html"):
    context = {}
    edgetypes = EdgeType.objects.all()
    context['edgetype_items'] = edgetypes    
    return render_to_response(template_name, context, context_instance=RequestContext(request))


def single_edgetype(request, edgetype_id, template_name="modelrelationship/single_edgetype.html"):
    context = {}
    edgetype = EdgeType.objects.all().get(id=edgetype_id)
    context['edgetype'] = edgetype        
    return render_to_response(template_name, context, context_instance=RequestContext(request))
    
def new_edgetype(request, form_class=EdgeTypeForm, template_name="modelrelationship/new_edgetype.html"):
    context = {}    
    parent_typeid=None
    child_typeid=None
    for item in request.GET.items():
        if item[0] == 'parent_type':
            parent_typeid=item[1]
        if item[0] == 'child_type':
            child_typeid=item[1]
    
    new_form = form_class(parent_typeid=parent_typeid,child_typeid=child_typeid)
    context['form'] = new_form
    if request.method == 'POST':
        if request.POST["action"] == "create":
            new_form = form_class(parent_typeid,child_typeid,request.POST)
            if new_form.is_valid():                
                newedgetype = new_form.save(commit=False)
                newedgetype.save()
                return HttpResponseRedirect(reverse('view_all_edgetypes', kwargs= {}))

    return render_to_response(template_name, context, context_instance=RequestContext(request))            
    

def new_edge(request, edgetype_id, form_class=EdgeForm, template_name="modelrelationship/new_edge.html"):
    context = {}    
    new_form = form_class(edgetype_id)
    
    parent_item_id=None
    child_item_id=None
    print request.GET.items()
    for item in request.GET.items():
        if item[0] == 'parent_id':
            parent_item_id=item[1]                    
        if item[0] == 'child_id':
            child_item_id=item[1]    

    new_form = form_class(edgetype_id, parent_item_id,child_item_id)     
    context['form'] = new_form                           
    if request.method == 'POST':
        if request.POST["action"] == "create":                        
            new_form = form_class(edgetype_id, parent_item_id,child_item_id,request.POST)
            if new_form.is_valid():                
                newedgetype = new_form.save(commit=False)
                newedgetype.save()
                return HttpResponseRedirect(reverse('view_all_edgetypes', kwargs= {}))

    return render_to_response(template_name, context, context_instance=RequestContext(request))            


def all_edges(request, template_name="modelrelationship/all_edges.html"):
    context = {}
    edges = Edge.objects.all()
    context['edge_items'] = edges    
    return render_to_response(template_name, context, context_instance=RequestContext(request))


def single_edge(request, edge_id, template_name="modelrelationship/single_edge.html"):
    context = {}
    edge = Edge.objects.all().get(id=edge_id)
    context['edge'] = edge        
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def view_content_item(request,template_name="modelrelationship/single_content_item.html"):
    context = {}
    contenttype_id = -1
    content_id =-1
    
    for item in request.GET.items():
        if item[0] == 'content_type':
            contenttype_id=item[1]
        if item[0] == 'content_id':
            content_id=item[1]
    
    ctype = ContentType.objects.all().get(id=contenttype_id)
    context['content_type'] = ctype
    content_instance = ctype.model_class().objects.all().get(id=content_id)
    context['content_instance'] =  content_instance
    
    parent_edgetypes = EdgeType.objects.all().filter(parent_type=ctype)
    
    parent_edges = {}
    for edgetype in parent_edgetypes:
        parent_edges[edgetype] = Edge.objects.all().filter(relationship=edgetype, parent_type=ctype,parent_id=content_instance.id)
    
    child_edgetypes = EdgeType.objects.all().filter(child_type=ctype)
    
    child_edges = {}
    for edgetype in child_edgetypes:
        child_edges[edgetype] = Edge.objects.all().filter(relationship=edgetype, child_type=ctype,child_id=content_instance.id)
    
    
    context['parent_edges'] = parent_edges
    context['child_edges'] = child_edges    
    
    context['parent_edgetypes'] = EdgeType.objects.all().filter(parent_type=ctype)
    context['child_edgetypes'] = EdgeType.objects.all().filter(child_type=ctype)
    
            
    return render_to_response(template_name, context, context_instance=RequestContext(request))
    
