from django.db.models import Model
from mptt.models import TreeForeignKey

class NestedLocation(models.Model):
    tree_parent = TreeForeignKey('self', null=True, blank=True, related_name='tree_children')
