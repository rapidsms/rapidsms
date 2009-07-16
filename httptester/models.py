from django.db import models

class Permissions(models.Model):
    '''This is a fake model that has nothing in it, because
       django expects all app-level permissions to be in
       a model'''
    
    class Meta:
        # the permission required for this tab to display in the UI
        permissions = (
            ("can_view", "Can view"),
        )