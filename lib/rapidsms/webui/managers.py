#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


class RecursiveManager(models.Manager):
    """Provides a method to flatten a recursive model (a model which has a ForeignKey field linked back
       to itself), in addition to the usual models.Manager methods. This Manager queries the database
       only once (unlike select_related), and sorts them in-memory. Obivously, this efficiency comes
       at the cost local inefficiency -- O(n^2) -- but that's still preferable to recursively querying
       the database."""
    
    def flatten(self, via_field="parent_id"):
        all_objects = list(self.all())
        
        def pluck(pk=None, depth=0):
            output = []
            
            for object in all_objects:
                if getattr(object, via_field) == pk:
                    output += [object] + pluck(object.pk, depth+1)
                    object.depth = depth
            
            return output
        return pluck()
