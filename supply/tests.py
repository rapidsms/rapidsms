from rapidsms.tests.scripted import TestScript
from apps.form.models import *
from apps.reporters.models import *
import apps.reporters.app as reporter_app
import apps.nigeria.app as nigeria_app
import apps.form.app as form_app
from app import App
from models import *

class TestApp (TestScript):
    apps = (reporter_app.App, App,form_app.App, nigeria_app.App )
    fixtures = ['nigeria_llin', 'kano_locations']
    
    def setUp(self):
        TestScript.setUp(self)
        # have to initialize the backend for the reporters app to function properly
        title = self.backend.name
        try:
            PersistantBackend.objects.get(title=title)
        except PersistantBackend.DoesNotExist:
            PersistantBackend(title=title).save()

    def testScript(self):
        mismatched_amounts = """
            8005552222 > llin register 20 sm mister sender 
            8005552222 < Hello msender! You are now registered as Stock manager at KANO State.
            8005551111 > llin register 2027 sm mister recipient
            8005551111 < Hello mrecipient! You are now registered as Stock manager at KURA LGA.
            8005552222 > llin issue from 20 to 2027 11111 200 1800
            8005552222 < Received report for LLIN issue: origin=KANO, dest=KURA, waybill=11111, amount=200, stock=1800. If this is not correct, reply with CANCEL
            8005551111 > llin receive from 20 to 2027 11111 150 500
            8005551111 < Received report for LLIN receive: origin=KANO, dest=KURA, waybill=11111, amount=150, stock=500. If this is not correct, reply with CANCEL
            """
        self.runScript(mismatched_amounts)

        sender = Reporter.objects.get(alias="msender")
        recipient = Reporter.objects.get(alias="mrecipient")

        issue = PartialTransaction.objects.get(origin__name="KANO",\
           destination__name="KURA", shipment_id="11111",\
           domain__code="LLIN", type="I", reporter__pk=sender.pk)

        receipt = PartialTransaction.objects.get(origin__name__iexact="KANO",\
           destination__name__iexact="KURA", shipment_id="11111",\
           domain__code__iexact="LLIN", type="R", reporter__pk=recipient.pk)
        
        origin_stock = Stock.objects.get(location__name__iexact="KANO",\
            domain__code__iexact="LLIN")
        dest_stock = Stock.objects.get(location__name__iexact="KURA",\
            domain__code__iexact="LLIN")
        
        # everything in its right place
        self.assertEqual(sender.location, issue.origin)
        self.assertEqual(recipient.location, issue.destination)
        self.assertEqual(sender.location, receipt.origin)
        self.assertEqual(recipient.location, receipt.destination)

        # stocks created with correct balance
        self.assertEqual(issue.stock, origin_stock.balance)
        self.assertEqual(receipt.stock, dest_stock.balance)

        # issue and receipt have been matched into a transaction
        self.assertEqual(issue.status, 'C')
        self.assertEqual(issue.status, receipt.status)
        first_transaction = Transaction.objects.get(domain__code__iexact="LLIN",\
            amount_sent=issue.amount, amount_received=receipt.amount,\
            issue=issue, receipt=receipt)

        # mister recipient received 50 fewer nets than were sent by mister sender
        self.assertNotEqual(issue.amount, receipt.amount)
        self.assertNotEqual(first_transaction.amount_sent, first_transaction.amount_received)
        self.assertEqual(first_transaction.flag, 'A') 

        # mister recipient realizes his error and resends with correct amount
        amendment = """
            8005551111 > llin receive from 20 to 2027 11111 200 500
            8005551111 < Received report for LLIN receive: origin=KANO, dest=KURA, waybill=11111, amount=200, stock=500. If this is not correct, reply with CANCEL
            """
        self.runScript(amendment)

        # pick fresh sprouts of these from the database
        receipt = PartialTransaction.objects.get(pk=receipt.pk)
        first_transaction = Transaction.objects.get(pk=first_transaction.pk)

        # mister recipient's original receipt should now be amended and
        # the first transaction should be flagged as incorrect
        self.assertEqual(receipt.status, 'A')
        self.assertEqual(first_transaction.flag, 'I')

        # mister recipient's amendment
        second_receipt = PartialTransaction.objects.get(origin__name__iexact="KANO",\
           destination__name__iexact="KURA", shipment_id="11111",\
           domain__code__iexact="LLIN", type="R", reporter=recipient, status="C")

        # make sure this is a new one
        self.assertNotEqual(second_receipt.pk, receipt.pk)

        # make sure a new transaction was matched
        second_transaction = Transaction.objects.get(domain__code__iexact="LLIN",\
            amount_sent=issue.amount, amount_received=second_receipt.amount,\
            issue=issue, receipt=second_receipt)

        # make sure this is a new one
        self.assertNotEqual(first_transaction.pk, second_transaction.pk)

        # the new transaction should not be flagged with either of these
        self.assertNotEqual(second_transaction.flag, 'I')
        self.assertNotEqual(second_transaction.flag, 'A')

        # new figures should add up
        self.assertEqual(issue.amount, second_receipt.amount)
        self.assertEqual(second_transaction.amount_sent, second_transaction.amount_received)

    def testUnregisteredSubmissions(self):
        # send a form from an unregistered user and assure it is accepted
        unregistered_submission = """
            supply_tus_1 > llin issue from 20 to 2027 11111 200 1800
            supply_tus_1 < Received report for LLIN issue: origin=KANO, dest=KURA, waybill=11111, amount=200, stock=1800. If this is not correct, reply with CANCEL. Please register your phone
            """
        self.runScript(unregistered_submission)
        
        # check that the connection object in the transaction is set properly
        connection = PersistantConnection.objects.get(identity="supply_tus_1")
        issue = PartialTransaction.objects.get(origin__name="KANO",\
           destination__name="KURA", shipment_id="11111",\
           domain__code="LLIN", type="I", connection=connection)
        
        # check that the reporter is empty
        self.assertFalse(issue.reporter)
