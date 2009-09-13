#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from django.contrib.contenttypes import generic
from modelrelationship.models import *

class EdgeParentInline(generic.GenericTabularInline):
    ct_field='parent_type'
    ct_fk_field = 'parent_id'
    model = Edge 
    
class EdgeChildInline(generic.GenericTabularInline):
    ct_field='child_type'
    ct_fk_field = 'child_id'
    model = Edge

class EdgeTypeParentInline(generic.GenericTabularInline):
    ct_field= 'parent_type'    
    model = EdgeType



class EdgeTypeAdmin(admin.ModelAdmin):
    list_display = ('name','description','directional','parent_type','child_type')
    list_filter = ['directional']    
    #inlines = [ EdgeParentInline, EdgeChildInline,]
    pass


class EdgeAdmin(admin.ModelAdmin):
    list_display = ('parent_type','parent','relationship','child',)
    list_filter = ['relationship', 'parent_type','parent_id','child_type','child_id',]    

admin.site.register(EdgeType,EdgeTypeAdmin)
admin.site.register(Edge,EdgeAdmin)
admin.site.register(NewEdge)
admin.site.register(NewEdgeType)
