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
        pending = self._partial_transaction_from_form(message, form_entry)
        transaction = self._match_partial_transaction(pending)
        
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
    def _partial_transaction_from_form(self, message, form_entry):
        print("creating pending")
        pending = PartialTransaction()
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
        # gather partial transactions from the same place to the same place with
        # for the same stuff with the same waybill before we save the new one
        # TODO checking for same phone currently, should we not?
        # TODO handle confirmed ammendments differently -- update stock!
        partials_to_ammend = PartialTransaction.objects.filter(origin=pending.origin,\
            destination=pending.destination, shipment_id=pending.shipment_id,\
            domain=pending.domain, type=pending.type,  phone=pending.phone)
        # if this is an ammendment, set the others as ammended
        if partials_to_ammend is not None:
                partials_to_ammend.update(status = "A")

        pending.save()
        return pending
    
    def _match_partial_transaction(self, partial):
        # gather pending, partial transactions that are not the same type
        # as this one (e.g., look at receipts if this one is an issue)
        orphans = PartialTransaction.objects.filter(status='P').exclude(pk=partial.id)\
            .exclude(type=partial.type)
        # save pending transactions that appear in all of these sets
        matches = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'shipment_id')
        if len(matches) != 0:
            print("MATCHES!")
            # there should only be one...
            if len(matches) == 1:
                return self._new_transaction(partial, matches.pop())
            else:
                # ... but if there are many, filter these matches by amount
                print("TOO MANY MATCHES!")
                amount_matches = self._match_orphans_by(partial, matches, 'amount')
                if len(amount_matches) != 0:
                    if len(amount_matches) == 1:
                        return self._new_transaction(partial, amount_matches.pop())
        else:
            # no matches yet, so lets filter orig orphans by origin, dest, and amount
            # in case we have a waybill typo
            wrong_waybill_match = self._matches_orphans_by(partial, orphans, 'origin', 'destination', 'amount')
            if len(wrong_waybill_match) != 0:
                if len(wrong_waybill_matches) == 1:
                    return self._new_transaction(partial, wrong_waybill_matches.pop())

    def _match_orphans_by(self, partial, orphans, *attributes):
        print("matching orphans")
        filtered_orphans = orphans
        for a in attributes:
            param = { a : getattr(partial, a) }
            # update orphans with the intersection of itself
            # and itself filtered by an attribute
            filtered_orphans &= filtered_orphans.filter(**param)
        return orphans 


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
    
