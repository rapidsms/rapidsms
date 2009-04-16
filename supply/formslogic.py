#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from models import *
from apps.form.utils import *

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
        transaction = self._match_pending_transaction(pending)
        
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
        print("creating pending")
        pending = PendingTransaction()
        pending.domain = form_entry.domain
        pending.date = form_entry.date
        to_use = self._form_lookups[form_entry.form.type]
        pending.type = to_use["type"]
        for token_entry in form_entry.tokenentry_set.all():
            if to_use.has_key(token_entry.token.abbreviation):
                setattr(pending, to_use[token_entry.token.abbreviation], token_entry.data)
        # TODO hack around locations for now
        pending.origin = Location.objects.all()[0]
        pending.destination = Location.objects.all()[1]
        pending.status = "P"
        pending.phone = message.connection.identity
        # gather pending transactions from the same place to the same place with
        # for the same stuff with the same waybill
        # TODO checking for same phone currently, should we not?
        pending_to_ammend = PendingTransaction.objects.filter(origin=pending.origin,\
            destination=pending.destination, shipment_id=pending.shipment_id,\
            domain=pending.domain, status=pending.status, type=pending.type,\
            phone=pending.phone)
        # if this is an ammendment, set the others as ammended
        if pending_to_ammend is not None:
                pending_to_ammend.update(status = "A")

        pending.save()
        return pending
    
    def _match_pending_transaction(self, pending):
        # gather pending transactions that are pending and not of the type
        # of this one.
        orphans_for_origin = PendingTransaction.objects.filter(origin=pending.origin,\
            status='P').exclude(pk=pending.id).exclude(type=pending.type)
        orphans_for_dest = PendingTransaction.objects.filter(destination=pending.destination,\
            status='P').exclude(pk=pending.id).exclude(type=pending.type)
        orphans_for_waybill = PendingTransaction.objects.filter(shipment_id=pending.shipment_id,\
            status='P').exclude(pk=pending.id).exclude(type=pending.type)

        # save pending transactions that appear in all of these sets
        matches = orphans_for_origin & orphans_for_dest & orphans_for_waybill 
        if len(matches) != 0:
            print("MATCHES!")
            # there should only be one...
            if len(matches) == 1:
                return self._new_transaction(pending, matches[0])
            else:
                print("TOO MANY MATCHES!")

    def _new_transaction(self, issue, receipt):
        # create a new shipment
        # TODO should we create a shipment for each waybill we received 
        # i.e., for incomplete transactions?
        shipment = Shipment.objects.create(origin=receipt.origin, destination=issue.destination,\
            sent=issue.date, received=receipt.date, shipment_id=issue.shipment_id)
        transaction = Transaction.objects.create(domain=issue.domain, amount_sent=issue.amount,\
            amount_received=receipt.amount,issue=issue, receipt=receipt, shipment=shipment)
        print("NEW TRANSACTION")
        # set the pending transactions to complete
        issue.status="C"
        issue.save()
        receipt.status="C"
        receipt.save()
        return transaction
    
