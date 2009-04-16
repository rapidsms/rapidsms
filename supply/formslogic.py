#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *

class SupplyFormsLogic:
    ''' This class will hold the supply-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
       
    def validate(self, *args, **kwargs):
        print "Supply validated!"
        print "You passed in %s" % args[0]
        
    def actions(self, *args, **kwargs):
        print "Supply actions!"
        print "You passed in %s and %s" % (args[0], args[1])
        message = args[0]
        form_entry = args[1]
        
        # I'm just going to hard code this here.  This should possibly be moved
        # Since actions was called we assume validation passed.  
        # The first thing we do is create a PendingTransaction object and save it
        pending = self._pending_transaction_from_form(message, form_entry)
        
    # Just hard coding this for now.  We might want to revisit this.
    _form_lookups = {"issue" : {
                                #"origin" : "origin", 
                                #"dest" : "destination", 
                                "type" : "I",
                                "waybill" : "shipment_id", 
                                "sent" : "amount", 
                                "stock" : "stock", 
                                 
                                }, 
                     "receive" : {
                                  #"origin" : "origin", 
                                  #"dest" : "destination", 
                                  "type" : "R",
                                  "waybill" : "shipment_id", 
                                  "received" : "amount", 
                                  "stock" : "stock", 
                                  }
                     }
    def _pending_transaction_from_form(self, message, form_entry):
        #print "creating transaction"
        pending = PendingTransaction()
        pending.domain = form_entry.domain
        pending.date = form_entry.date
        to_use = self._form_lookups[form_entry.form.type]
        pending.type = to_use["type"]
        for token_entry in form_entry.tokenentry_set.all():
            if to_use.has_key(token_entry.token.abbreviation):
                setattr(pending, to_use[token_entry.token.abbreviation], token_entry.data)
            #pass
        #hack around locations for now
        pending.origin = Location.objects.all()[0]
        pending.destination = Location.objects.all()[1]
        pending.status = "P"
        pending.phone = message.connection.identity
        pending.save()
    #reporter = models.ForeignKey(Reporter)
    #origin = models.ForeignKey(Location)
    #destination = models.ForeignKey(Location, related_name='pending destination')
    #shipment_id = models.PositiveIntegerField(blank=True, null=True, help_text="Waybill number")
    #amount = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply shipped")
    #type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    #status = models.CharField(max_length=1, choices=STATUS_TYPES)
    
