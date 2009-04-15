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
        
    def _pending_transaction_from_form(self, message, form_entry):
        #print "creating transaction"
        pending = PendingTransaction()
        pending.domain = form_entry.domain
        pending.date = form_entry.date
        for token_entry in form_entry.tokenentry_set.all():
            #print token_entry
            pass
        pending.status = "P"
    #reporter = models.ForeignKey(Reporter)
    #origin = models.ForeignKey(Location)
    #destination = models.ForeignKey(Location, related_name='pending destination')
    #shipment_id = models.PositiveIntegerField(blank=True, null=True, help_text="Waybill number")
    #amount = models.PositiveIntegerField(blank=True, null=True, help_text="Amount of supply shipped")
    #type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    #status = models.CharField(max_length=1, choices=STATUS_TYPES)
    
