from django import template
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse

from modelrelationship.models import *
from django.contrib.contenttypes.models import ContentType
from types import ListType,TupleType

import modelrelationship.traversal as traversal

register = template.Library()


@register.simple_tag
def get_all_edgetypes_for_content(contenttype):    
    return ''

@register.simple_tag
def get_parent_edges_for_object(content_object):    
    return ''

@register.simple_tag
def get_child_edges_for_object(content_object):    
    return ''

@register.simple_tag
def get_parent_edgetypes_for_content(contenttype):    
    return ''

@register.simple_tag
def get_child_edgetypes_for_content(contenttype):    
    return ''

@register.simple_tag
def get_pedigree_for_content(content_object):
    return ''


@register.simple_tag
def get_full_children_for_content(content_object):
    return ''


@register.simple_tag
def get_siblings_for_content(content_object):
    return ''


def _get_recursive_ancestry(content_object):
    
    return obj

@register.simple_tag
def get_parent_breadcrumbs_for_edge(content_object):    
    return ''




class EdgeAncestryNode(template.Node):
    def __init__(self, content_object, context_name):
        self.edge = template.Variable(content_object)
        self.var_name = context_name
    def render(self, context):               
        #context[self.var_name] = AuxiliaryID.objects.all().filter(patient=self.patient)
        #[ancestry as list]
        context[self.var_name] = traversal.getFamilyTreeForObject(self.edge)        
        return ''

@register.tag('get_ancestors_for_obj')
def do_get_ancestors_for_obj(parser, token):
    #error_string = "%r tag must be of format {%% get_patient_identifiers for PATIENT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    error_string = "%r tag must be of format {%% get_ancestors_for_edge for EDGE as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    try:
        split = token.split_contents()        
    except ValueError:
        raise template.TemplateSyntaxError(error_string)
    if len(split) == 5:
        return EdgeAncestryNode(split[2],split[4])
    else:
        raise template.TemplateSyntaxError(error_string)

class EdgeDescendantsNode(template.Node):
    def __init__(self, content_object, context_name):
        self.obj = template.Variable(content_object)
        self.var_name = context_name
    def render(self, context):               
        #parent_edges[edgetype] = Edge.objects.all().filter(relationship=edgetype, parent_type=ctype,parent_id=content_instance.id)
        context[self.var_name] = traversal.getFullDescendantsForObject(self.obj)                                                
        return ''

@register.tag('get_ancestors_for_obj')
def do_get_descendants_for_obj(parser, token):
    #error_string = "%r tag must be of format {%% get_patient_identifiers for PATIENT as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    error_string = "%r tag must be of format {%% get_descendants_for_obj for EDGE as CONTEXT_VARIABLE %%}" % token.contents.split()[0]
    try:
        split = token.split_contents()        
    except ValueError:
        raise template.TemplateSyntaxError(error_string)
    if len(split) == 5:
        return EdgeDescendantsNode(split[2],split[4])
    else:
        raise template.TemplateSyntaxError(error_string)


def render_tree_as_table(arr, direction):
    #retstring += '&gt;&gt;&gt; <a href="%s">' % (reverse('view_current_patient', kwargs= {'patient_id': patient.id}))
    if len(arr) == 1:
        ctype = ContentType.objects.get_for_model(arr[0])
        return '<td><a href="%s?content_type=%s&content_id=%s">%s</a></td>' % (reverse('view_content_item', kwargs= {}),ctype.id,arr[0].id,arr[0])
    
    fullret = ''
    
    for item in arr:
        subitems = ''
        sublist = ''
        
        if isinstance(item,ListType):
            if len(item) > 1:    
                sublist += '\n<tr>'    
                sublist += render_tree_as_table(item,direction)
                sublist += '</tr>'
            else:                
                ctype = ContentType.objects.get_for_model(item[0])
                subitems += '<td>'
                subitems += '<a href="%s?content_type=%s&content_id=%s">%s</a>' % (reverse('view_content_item', kwargs= {}),ctype.id,item[0].id,item[0])         
                subitems += '</td>'            
        else:
            ctype = ContentType.objects.get_for_model(item)
            subitems += '<td>'
            subitems += '[<a href="%s?content_type=%s&content_id=%s">%s</a>]' % (reverse('view_content_item', kwargs= {}),ctype.id,item.id,item)         
            subitems += '</td>'
        
        if direction == 'children':
            fullret += subitems + sublist 
        else:
            fullret = sublist + subitems + fullret
    return fullret
        
def render_tree_as_ul(arr, direction):
    #retstring += '&gt;&gt;&gt; <a href="%s">' % (reverse('view_current_patient', kwargs= {'patient_id': patient.id}))

#    if len(arr) == 1:
#        ctype = ContentType.objects.get_for_model(arr[0])
#        return '<td><a href="%s?content_type=%s&content_id=%s">%s</a></td>' % (reverse('view_content_item', kwargs= {}),ctype.id,arr[0].id,arr[0])
#    
    fullret = ''
    
    for edge in arr:
        subitems = ''
        sublist = ''            
        
        if isinstance(edge,ListType):
            if len(edge) > 1:    
                sublist += '\n<ul>'    
                sublist += render_tree_as_table(edge,direction)
                sublist += '</ul>'
            else:                
                ctype = ContentType.objects.get_for_model(edge[0])
                subitems += '<li>'
                subitems += '<a href="%s?content_type=%s&content_id=%s">%s</a>' % (reverse('view_content_item', kwargs= {}),ctype.id,edge[0].id,edge[0])         
                subitems += '</li>'            
        else:            
            ctype = ContentType.objects.get_for_model(the_item)
            subitems += '<li>'
            subitems += '<a href="%s?content_type=%s&content_id=%s">%s</a>' % (reverse('view_content_item', kwargs= {}),ctype.id,the_item.id,edge)         
            subitems += '</li>'
        
        if direction == 'children':
            fullret += subitems + sublist 
        else:
            fullret = sublist + subitems + fullret
    return fullret
        
def render_edgetree_as_ul(arr, direction):
    #retstring += '&gt;&gt;&gt; <a href="%s">' % (reverse('view_current_patient', kwargs= {'patient_id': patient.id}))

#    if len(arr) == 1:
#        ctype = ContentType.objects.get_for_model(arr[0])
#        return '<td><a href="%s?content_type=%s&content_id=%s">%s</a></td>' % (reverse('view_content_item', kwargs= {}),ctype.id,arr[0].id,arr[0])
    
    fullret = ''
    
    prior_edgetype = None
    group_edge = False
    
    
    for edges in arr:
        subitems = ''
        sublist = ''
        edge = None
        do_continue = True       
        
        
        if isinstance(edges,ListType):
            #if len(edges) > 1:            
            sublist += '\n<ul>'    
            sublist += render_edgetree_as_ul(edges,direction)
            sublist += '</ul>'
            sublist += '</ul>'
            do_continue=False                  
        
        if do_continue:            
            if edge == None:            
                edge = edges
                    
            if edge.relationship != prior_edgetype:      
                if group_edge:
                    group_edge = False
                    subitems +=  '</ul>'              
                prior_edgetype = edge.relationship
                subitems += '<li>'
                subitems += edge.relationship.name
                subitems +=  '<ul>'
                group_edge = True            
                            
            subitems += '\t<li>'
            if direction == 'children':
                subitems += '<a href="%s?content_type=%s&content_id=%s">%s</a>' % (reverse('view_content_item', kwargs= {}),edge.child_type.id,edge.child_object.id,edge.child_object)         
            else:                
                subitems += '<a href="%s?content_type=%s&content_id=%s">%s</a>' % (reverse('view_content_item', kwargs= {}),edge.parent_type.id,edge.parent_object.id,edge.parent_object)
            subitems += '\t</li>'                        
            subitems += '</li>'    
        
        if direction == 'children':
            fullret += subitems + sublist 
        else:
            fullret += subitems + sublist
    return fullret


#getAncestorEdgesForObject
#getDescendentEdgesForObject


@register.simple_tag
def get_descendents(content_obj):
    descendents = traversal.getDescendentEdgesForObject(content_obj)
    if len(descendents) > 0:
        return '<div class="descendants"><h3>Children</h3><h4>' + str(content_obj) + '</h4><ul>' + render_edgetree_as_ul(descendents,'children') + '</ul></div>'
    else:
        return '<div class="parents"><h4>No children</h4></div>'

@register.simple_tag
def get_ancestors(content_obj):
    
    ancestors = traversal.getAncestorEdgesForObject(content_obj)    
    if len(ancestors) > 0:
        return '<div class="parents"><h3>Parents</h3><h4>' + str(content_obj) + '</h4><ul>' + render_edgetree_as_ul(ancestors,'parents') + '</ul></div>'
    else:
        return '<div class="parents"><h4>No ancestors</h4></div>'    
    





