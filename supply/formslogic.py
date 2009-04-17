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
        self._match_partial_transaction(pending)
        
    # Just hard coding this for now.  We might want to revisit this.
    _form_lookups = {"issue" : {
                                "origin" : "origin", 
                                "dest" : "destination", 
                                "type" : "I",
                                "waybill" : "shipment_id", 
                                "sent" : "amount", 
                                "stock" : "stock", 
                                 
                                }, 
                     "receive" : {
                                  "origin" : "origin", 
                                  "dest" : "destination", 
                                  "type" : "R",
                                  "waybill" : "shipment_id", 
                                  "received" : "amount", 
                                  "stock" : "stock", 
                                  }
                     }
    _foreign_key_lookups = {"Location" : "code"
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
                field_name = to_use[token_entry.token.abbreviation]
                # this is sillyness.  this gets the model type from the metadata
                # and if it's a foreign key then "rel" will be non null
                foreign_key = pending._meta.get_field_by_name(field_name)[0].rel
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
                        setattr(pending, field_name, fk_instance)
                    except fk_class.DoesNotExist:
                        # ah well, we tried.  Is this a real error?  It might be, but if this
                        # was a required field then the save() will fail
                        pass
                else:
                    setattr(pending, to_use[token_entry.token.abbreviation], token_entry.data)
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
        remainder = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'shipment_id', 'amount')
        if remainder is not None:
            print('remainder')
            # check for mismatched amount 
            amount_remainder = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'shipment_id')
            if amount_remainder is not None:
                print('amount remainder')
                # no matches yet, so lets filter orig orphans by origin, dest, and amount
                # in case we have a waybill typo
                wrong_waybill = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'amount')


    def _match_orphans_by(self, partial, orphans, *attributes):
        print("matching orphans")
        filtered_orphans = orphans
        for a in attributes:
            param = { a : getattr(partial, a) }
            # update orphans with the intersection of itself
            # and itself filtered by an attribute
            filtered_orphans &= filtered_orphans.filter(**param)

        print(filtered_orphans)
        if filtered_orphans.count() != 0:
            if filtered_orphans.count() == 1:
                self._new_transaction(partial, filtered_orphans[0], attributes)
                return None
            else:
                return filtered_orphans
        else:
            return 0


    def _new_transaction(self, issue, receipt, *matched_by):
        # create a new shipment
        # TODO should we create a shipment for each waybill we received 
        # i.e., for incomplete transactions?
        shipment = Shipment.objects.create(origin=receipt.origin, destination=issue.destination,\
            sent=issue.date, received=receipt.date, shipment_id=issue.shipment_id)
        transaction = Transaction.objects.create(domain=issue.domain, amount_sent=issue.amount,\
            amount_received=receipt.amount,issue=issue, receipt=receipt, shipment=shipment)
        print("NEW TRANSACTION")
        print(matched_by)
        # set the pending transactions to complete
        issue.status="C"
        issue.save()
        receipt.status="C"
        receipt.save()
        return transaction
    
