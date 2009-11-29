#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rapidsms.message import StatusCodes
from models import *
from form.utils import *
from form.formslogic import FormsLogic

class SupplyFormsLogic(FormsLogic):
    ''' This class will hold the supply-specific forms logic.
        I'm not sure whether this will be the right structure
        this was just for getting something hooked up '''
       
    def validate(self, *args, **kwargs):
        pass 
            
        
    def actions(self, *args, **kwargs):
        #print "Supply actions!"
        #print "You passed in %s and %s" % (args[0], args[1])
        message = args[0]
        form_entry = args[1]
        
        # I'm just going to hard code this here.  This should possibly be moved
        # Since actions was called we assume validation passed.  
        # The first thing we do is create a PartialTransaction object and save it
        pending = self._partial_transaction_from_form(message, form_entry)
        
        # Update stock balance and flag this partial
        # if reported balance does not equal expected balance
        self._update_stock_balance(pending)

        # Attempt to match this pending, partial transaction to another
        # and create a new transaction
        self._match_partial_transaction(pending)
        
    #TODO Just hard coding this for now.  We might want to revisit this.
    _form_lookups = {"issue" : {
                                "origin" : "origin", 
                                "dest" : "destination", 
                                "type" : "I",
                                "waybill" : "shipment_id", 
                                "amount" : "amount", 
                                "stock" : "stock", 
                                 
                                }, 
                     "receive" : {
                                  "origin" : "origin", 
                                  "dest" : "destination", 
                                  "type" : "R",
                                  "waybill" : "shipment_id", 
                                  "amount" : "amount", 
                                  "stock" : "stock", 
                                  }
                     }
    _foreign_key_lookups = {"Location" : "code" 
                           }
    def _partial_transaction_from_form(self, message, form_entry):
        if not self._form_lookups.has_key(form_entry.form.code.abbreviation):
            # if this form isn't something we know about then return immediately
            return
        #print("creating partial")
        this_form_lookups = self._form_lookups[form_entry.form.code.abbreviation]
        partial = self._model_from_form(message, form_entry, PartialTransaction, 
                                        this_form_lookups, self._foreign_key_lookups)
        # if the reporter isn't set then populate the connection object.
        # this means that at least one (actually exactly one) is set
        # the method above sets this property in the partial transaction
        # if it was found.
        if not hasattr(partial, "reporter") or not partial.reporter:
            partial.connection = message.persistant_connection
            response = ""
        # personalize response if we have a registered reporter
        else:
            response = "Thank you %s. " % (partial.reporter.first_name)
        partial.domain = form_entry.domain
        partial.date = form_entry.date
        partial.type = this_form_lookups["type"]
        partial.status = "P"
        # gather partial transactions from the same place to the same place with
        # for the same stuff with the same waybill before we save the new one
        all_partials_to_amend = PartialTransaction.objects.filter(origin=partial.origin,\
            destination=partial.destination, shipment_id=partial.shipment_id,\
            domain=partial.domain, type=partial.type)

        # we're going to deal with confirmed partials separately
        confirmed_partials_to_amend = all_partials_to_amend.filter(status = 'C')
        partials_to_amend = all_partials_to_amend.exclude(status = 'C')

        # if we are going to amend a confirmed partial, 
        # find the transaction it belongs to, flag it as incorrect, 
        # and set its partial transactions as pending or ammended
        # (depending on what type of partial we have just received)
        for p in confirmed_partials_to_amend:
            #print('we have confirmation')
            transactions = p.transactions
            # there should only ever be one transaction per partial,
            # but p.transactions will always return a queryset
            for t in transactions:
                #TODO kill me now
                t.flag = 'I'
                if partial.type == 'I':
                    t.issue.status = 'A'
                    t.receipt.status = 'P'
                if partial.type == 'R':
                    t.issue.status = 'P'
                    t.receipt.status = 'A'
                t.receipt.save()
                t.issue.save()
                t.save()

        # if this is an ammendment, set the others as ammended
        if partials_to_amend is not None:
                partials_to_amend.update(status = "A")

        partial.save()
        response = response + "Received report for %s %s: origin=%s, dest=%s, waybill=%s, amount=%s, stock=%s" % (
             partial.domain.code.abbreviation.upper(), form_entry.form.code.abbreviation.upper(), partial.origin, partial.destination, partial.shipment_id, partial.amount, partial.stock)  
        message.respond(response, StatusCodes.OK)
        if not partial.reporter:
            message.respond("Please register your phone.")
        self._notify_counterparty(partial)
        return partial

    def _notify_counterparty(self, partial):
        #TODO
        if partial.type == 'I':
            pass
        elif partial.type == 'R':
            pass 
    
    def _match_partial_transaction(self, partial):
        #print('match partial transaction')
        # gather pending, partial transactions that are not the same type
        # as this one (e.g., look at receipts if this one is an issue)
        orphans = PartialTransaction.objects.filter(status='P').exclude(pk=partial.id)\
            .exclude(type=partial.type)
        # TODO? this flow control is wacky, but allows for relatively fine flow control
        # e.g., we could call _match_orphans_by again with different attributes on
        # filtered_orphans previously returned by _match_orphans_by
        
        # save pending transactions that appear in all of these sets
        remainder = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'shipment_id', 'amount')
        if remainder is not None:
            #print('remainder')
            # check for mismatched amount 
            amount_remainder = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'shipment_id')
            if amount_remainder is not None:
                #print('amount remainder')
                # no matches yet, so lets filter orig orphans by origin, dest, and amount
                # in case we have a waybill typo
                wrong_waybill = self._match_orphans_by(partial, orphans, 'origin', 'destination', 'amount')


    def _match_orphans_by(self, partial, orphans, *attributes):
        ''' Given a target partial transaction and a queryset of other
            partial transactions, attempt to match into a complete 
            transaction with respect to whichever attributes are given.
            Returns None if _new_transaction is successful and otherwise
            returns the remaining filtered_orphans matched on these attributes.'''
        #print("matching orphans")
        filtered_orphans = orphans

        # intersect filtered_orphans destructively to narrow down possible matches
        for a in attributes:
            param = { a : getattr(partial, a) }
            # update orphan queryset with the intersection of 
            # itself and itself filtered by an attribute
            filtered_orphans &= filtered_orphans.filter(**param)

        #print(filtered_orphans)
        if filtered_orphans.count() != 0:
            if filtered_orphans.count() == 1:
                # try to make a new transaction with this orphan, pass along
                # the attributes we used to match in case someone wants to know
                # 
                # return None if successful so _match_partial_transactions 
                # breaks from its cascading matching attempts
                # TODO i am fed up with these stupid partial types
                # TODO seriously. this shit is getting old.
                if partial.type == 'R':
                    transaction = self._new_transaction(filtered_orphans[0], partial, attributes)
                elif partial.type == 'I':
                    transaction = self._new_transaction(partial, filtered_orphans[0], attributes)
                if transaction:
                    return None
            else:
                # if we have several filtered_orphans by these attributes
                # return them in case _match_partial_transactions wants
                # to recurse on these filtered_orphans with differnt attributes
                return filtered_orphans
        else:
            # if we have zero filtered_orphans, return 0 so
            # _match_partial_transactions can try again with a different
            # combination of attributes
            return 0


    def _new_transaction(self, issue, receipt, *matched_by):
        ''' Create a Shipment and then attempt to create a new transaction from 
            two partial transactions. Mark partials as confirmed if stocks are
            updated successfully and flag Transaction if amounts or shipment_ids 
            disagree.'''
        # create a new shipment
        shipment = Shipment.objects.create(origin=receipt.origin, destination=issue.destination,\
            sent=issue.date, received=receipt.date, shipment_id=issue.shipment_id)
        transaction = Transaction(domain=issue.domain, amount_sent=issue.amount,\
            amount_received=receipt.amount,issue=issue, receipt=receipt, shipment=shipment)
        #print("NEW TRANSACTION")
        #print(matched_by)
        
        # set the pending transactions to confirmed 
        issue.status="C"
        issue.save()
        receipt.status="C"
        receipt.save()
        
        # if amount issued does not match amount received, set flag
        if int(issue.amount) != int(receipt.amount):
            transaction.flag = 'A'
        # if issue's shipment_id does not match receipt's shipment_id, set flag
        #
        # Note: a transaction can have only one flag. Two 
        # partial transactions with both mismatched amounts and shipment_ids
        # should not be sent to this method
        elif int(issue.shipment_id) != int(receipt.shipment_id):
            transaction.flag = 'W'
        
        transaction.save()
        return transaction 
    
    def _update_stock_balance(self, partial):
        ''' Update stock balance based on reported balance.
            Flag partial transaction if they don't add up to the
            estimated/expected balance. Returns True if updated.'''
        #print('update stock balance')
        if partial.type == 'I':
            # get or create stock at origin if this is an issue partial
            stock, created = Stock.objects.get_or_create(location=partial.origin, domain=partial.domain)
        elif partial.type == 'R':
            # get or create stock at destination if this is receipt partial
            stock, created = Stock.objects.get_or_create(location=partial.destination, domain=partial.domain)
            
        # update balance with newly reported balance
        stock.balance = partial.stock
        stock.save()
        if not created:
            # if we are updating an existing stock, flag issue
            # if reported stock does not match expected balance
            self._adjust_expectations(partial, stock)
        return True

    def _adjust_expectations(self, partial, stock):
        expected_balance = int(stock.balance) - int(partial.amount)
        if int(partial.stock) != expected_balance:
            partial.flag = 'S'
            partial.save()
