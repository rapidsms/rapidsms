#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *

class NigeriaFormsLogic:
    ''' This class will hold the nigeria-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
       
    def validate(self, *args, **kwargs):
        print "Nigeria validated!"
        print "You passed in %s" % args[0]
        message = args[0]
        if not message.reporter:
            return [ "You must register your phone before submitting data" ]
        
        
    _form_lookups = {"nets" : {
                                "class" : NetDistribution, 
                                "netloc" : "location", 
                                "distributed" : "distributed", 
                                "expected" : "expected", 
                                "actual" : "actual",
                                "discrepancy" : "discrepancy", 
                                }, 
                     "net" : {    "class" : CardDistribution, 
                                  "couploc" : "location", 
                                  "settlements" : "settlements", 
                                  "people" : "people", 
                                  "netcards" : "distributed",
                                  }
                     }
        
    _foreign_key_lookups = {"Location" : "code" }

    def actions(self, *args, **kwargs):
        print "Nigeria actions!"
        print "You passed in %s" % args[0]
        message = args[0]
        form_entry = args[1]
        # this borrows a lot from supply.  I think we can make this a utility call
        to_use = self._form_lookups[form_entry.form.type]
        form_class = to_use["class"]
        instance = form_class()
        for token_entry in form_entry.tokenentry_set.all():
            if to_use.has_key(token_entry.token.abbreviation):
                field_name = to_use[token_entry.token.abbreviation]
                # this is sillyness.  this gets the model type from the metadata
                # and if it's a foreign key then "rel" will be non null
                foreign_key = instance._meta.get_field_by_name(field_name)[0].rel
                if foreign_key:
                    # we can't just blindly set it, but we can get the class out 
                    fk_class = foreign_key.to
                    # and from there the name
                    fk_name = fk_class._meta.object_name
                    # and from there we look it up in our table
                    field = self._foreign_key_lookups[fk_name]
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
                    setattr(instance, to_use[token_entry.token.abbreviation], token_entry.data)
        instance.reporter = message.reporter
        instance.save()
        
        # this will be made more generic, but in the meantime this is quick and dirty
        
    
