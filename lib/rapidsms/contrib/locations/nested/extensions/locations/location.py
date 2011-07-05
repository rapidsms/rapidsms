from django.db import models

class NestedLocation(models.Model):
    tree_parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

    class Meta:
        abstract = True
