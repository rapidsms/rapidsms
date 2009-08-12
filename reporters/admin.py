#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from reporters.models import *
from django.core.urlresolvers import reverse

class ReporterAdmin(admin.ModelAdmin):
    list_display = ('id','alias','first_name', 'last_name')
    list_filter = []    


class PersistantConnectionAdmin(admin.ModelAdmin):
    list_display = ('id','backend','identity', 'reporter')
    list_filter = ['reporter','backend']

    
admin.site.register(Reporter, ReporterAdmin)


def reportergroup_members(self):
    
    #1.1 admin compatability
    #return ', '.join(['<a href="%s">%s</a>' % (reverse('admin:reporters_reporter_change', args=(x.id,)), x.alias) for x in self.reporters.all().order_by('id')])
    
    #1.0.x admin compatability
    return '<br> '.join(['<a href="%s">%s</a>' % (reverse( 'django-admin', args=["%s/%s/%s/" % ('reporters', 'reporter', x.id)]), x.alias) for x in self.reporters.all().order_by('id')])
    
    #return '<br> '.join([x.alias for x in self.reporters.all().order_by('alias')])
reportergroup_members.allow_tags = True
    
class ReporterGroupAdmin(admin.ModelAdmin):
    list_display = ('id','title','parent', 'description', reportergroup_members)
    list_filter = ['parent']

admin.site.register(Role)

admin.site.register(ReporterGroup, ReporterGroupAdmin)
admin.site.register(PersistantBackend)
admin.site.register(PersistantConnection, PersistantConnectionAdmin)
