#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *
from reporters.models import *


class FormsLogic:
    ''' This class holds method stubs and some utilities for 
        dealing with custom forms logic.  Others should inherit
        from this class and inject themselves into the forms app
        to provide their own custom logic.
    '''
       
    def validate(self, *args, **kwargs):
        ''' Perform any validation logic on the form.  This should 
            return False if everything passes, otherwise a list of 
            string representations of validation errors
        '''
        pass
        
    

    def actions(self, *args, **kwargs):
        ''' Any custom actions that need to be defined for the form.
            This will only get called if validation succeeds.  Actions
            may include responding to the message.  
        '''
        pass
    
    
    def _model_from_form(self, message, form_entry, model_class, field_lookups, foreign_key_lookups):
        ''' Constructs an instance of a model from form data and returns it.
            model_class is the class of the object to instantiate
            field_lookups is a dictionary of token values to fields they map to.
            foreign_key_lookups is a dictionary of class names to columns.
            Any time a field to be set is a foreign key, the token will be used
            to lookup an object whose column matches the one passed in.  
            For example, a foreign key to a location can be looked up by 
            location code.  
            In addition to this, this method will set the reporter in the model
            if the attribute exists in both the model and the message.
        '''
        # instantiate the instance from the passed in class.
        instance = model_class()
        for token_entry in form_entry.tokenentry_set.all():
            if field_lookups.has_key(token_entry.token.abbreviation):
                field_name = field_lookups[token_entry.token.abbreviation]
                # this is sillyness.  this gets the model type from the metadata
                # and if it's a foreign key then "rel" will be non null
                foreign_key = instance._meta.get_field_by_name(field_name)[0].rel
                if foreign_key:
                    # we can't just blindly set it, but we can get the class out 
                    fk_class = foreign_key.to
                    # and from there the name
                    fk_name = fk_class._meta.object_name
                    # and from there we look it up in our table
                    field = foreign_key_lookups[fk_name]
                    # get the object instance
                    filters = { field : token_entry.data }
                    try:
                        fk_instance = fk_class.objects.get(**filters)
                        setattr(instance, field_name, fk_instance)
                    except fk_class.DoesNotExist:
                        # ah well, we tried.  Is this a real error?  It might be, but if this
                        # was a required field then the save() will fail
                        pass
                else:
                    setattr(instance, field_lookups[token_entry.token.abbreviation], token_entry.data)
        if hasattr(message, "reporter"): 
            # this won't do anything special if this isn't a django property
            instance.reporter = message.reporter
        return instance
        
    
    
