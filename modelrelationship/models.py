from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class EdgeType(models.Model):
    #inline admin fixes:
    #http://www.thenestedfloat.com/articles/limiting-inline-admin-objects-in-django
    
    directional = models.BooleanField(default=True)    
     
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    
    child_type = models.ForeignKey(ContentType,related_name = 'child_type')    
    parent_type = models.ForeignKey(ContentType, related_name='parent_type')    

    class Meta:
        #verbose_name = _("Edge Type")
        #abstract=True  
        pass      
    
    def __unicode__(self):
        if self.directional:
            direction1 = "=="
            direction2 = '==>'
        else:
            direction1 = " <--"
            direction2 = "--> "
        
        return "EdgeType (%s [%s %s %s] %s :: %s)" % (self.parent_type,direction1, self.name,direction2,self.child_type,self.description)
    
    def as_edge(self):
        if self.directional:
            direction1 = "=="
            direction2 = '==>'
        else:
            direction1 = " <--"
            direction2 = "--> "
            
        return "%s %s %s" % (direction1, self.name, direction2)  
    def headline_display(self):
        return "%s" % (self.description)


class Edge(models.Model):    
    
    child_type = models.ForeignKey(ContentType, verbose_name=_('child content type'),related_name='child_type_set')
    child_id    = models.PositiveIntegerField(_('child object id'), db_index=True)
    child_object = generic.GenericForeignKey(ct_field='child_type',fk_field='child_id')    
        
    relationship = models.ForeignKey(EdgeType)
    
    parent_type = models.ForeignKey(ContentType, verbose_name=_('parent content type'),related_name='parent_type_set')
    parent_id    = models.PositiveIntegerField(_('parent object id'), db_index=True)
    parent_object = generic.GenericForeignKey(ct_field='parent_type', fk_field='parent_id')
    
        
    class Meta:
#    verbose_name = _("Edge")
#    abstract=True
        pass
   
    def __unicode__(self):
        return "[%s] %s [%s]" % (unicode(self.parent_object), unicode(self.relationship.as_edge()), unicode(self.child_object)) 
    
    @property
    def parent(self):
        return self.parent_object
    @property
    def child(self):
        return self.child_object    
    @property
    def pid(self):
        return self.parent_id
    @property
    def cid(self):
        return self.child_id
    @property
    def triple(self):
        return self.parent_object, self.relationship, self.child_object
    
    @property
    def ptype(self):
        return self.parent_type
    @property
    def ctype(self):
        return self.child_type
    
    def save(self):
        #todo, we need to fracking make sure that a few conditions exist:
        # that it's no dupe
        # no cycles!
        checkDupe = Edge.objects.all().filter(relationship=self.relationship,parent_type=self.parent_type,parent_id=self.parent_id,child_type=self.child_type,child_id=self.child_id)
        
        if len(checkDupe) != 0:
            raise Exception('Duplicate Edge exists')            
        
        super(Edge, self).save()
    
    def _get_allowable_objects(self):
        pass