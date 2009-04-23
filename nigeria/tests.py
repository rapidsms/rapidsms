from rapidsms.tests.scripted import TestScript
from apps.form.models import *
from apps.reporters.models import *
import apps.reporters.app as reporter_app
import apps.supply.app as supply_app
import apps.form.app as form_app
import apps.default.app as default_app
from app import App

class TestApp (TestScript):
    apps = (reporter_app.App, App,form_app.App, supply_app.App, default_app.App )
    fixtures = ['nigeria_llin', 'kano_locations']
    
    def setUp(self):
        TestScript.setUp(self)
        # have to initialize the backend for the reporters app to function properly
        title = self.backend.name
        try:
            PersistantBackend.objects.get(title=title)
        except PersistantBackend.DoesNotExist:
            PersistantBackend(title=title).save()
        
    def testFixtures(self):
        self._testKanoLocations()
        self._testForms()
        self._testRoles()
        
    def testScript(self):
        a = """
           8005551219 > llin register 20 dl crummy user
           8005551219 < Hello crummy! You are now registered as Distribution point team leader at KANO State.
           """
        self.runScript(a)
        # this should succeed because we just created him
        reporters = Reporter.objects.all()
        Reporter.objects.get(alias="cuser")
        dict = {"alias":"fail"}
        # make sure checking a non-existant user fails
        self.assertRaises(Reporter.DoesNotExist, Reporter.objects.get, **dict)     
        
    testRegistration = """
           8005551212 > llin my status
           8005551212 < Sorry, I don't know who you are.
           8005551212 > llin register 20 dl dummy user
           8005551212 < Hello dummy! You are now registered as Distribution point team leader at KANO State.
           8005551212 > llin my status
           8005551212 < I think you are are dummy.
         """
    
    testRegistrationErrors = """
           12345 > llin my status
           12345 < Sorry, I don't know who you are.
           12345 > llin register 45 DL hello world 
           12345 < Invalid form.  45 not in list of location codes
           12345 > llin my status
           12345 < Sorry, I don't know who you are.
           12345 > llin register 20 pp hello world 
           12345 < Invalid form.  pp not in list of role codes
           12345 > llin my status
           12345 < Sorry, I don't know who you are.
           12345 > llin register 6803 AL hello world 
           12345 < Invalid form.  6803 not in list of location codes. AL not in list of role codes
           12345 > llin my status
           12345 < Sorry, I don't know who you are.
         """
    
    testKeyword= """
           tkw_1 > llin register 20 dl keyword tester
           tkw_1 < Hello keyword! You are now registered as Distribution point team leader at KANO State.
           tkw_1 > llin nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > LLIN nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > lin nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > ILLn nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > ilin nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > ll nets 2001 123 456 78 90
           tkw_1 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           tkw_1 > llan nets 2001 123 456 78 90
           tkw_1 < Sorry, we didn't understand that message.  Please try again.
           tkw_1 > nets 2001 123 456 78 90
           tkw_1 < Sorry, we didn't understand that message.  Please try again.
        """
    
    testNets= """
           8005551213 > llin register 2001 lf net guy
           8005551213 < Hello net! You are now registered as LGA focal person at AJINGI LGA.
           8005551213 > llin nets 2001 123 456 78 90
           8005551213 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           8005551213 > llin nets 2001 123 456 78 
           8005551213 < Invalid form.  The following fields are required: discrepancy
         """
    
    testNetCards= """
           8005551214 > llin register 200201 lf card guy
           8005551214 < Hello card! You are now registered as LGA focal person at ALBASU CENTRAL Ward.
           8005551214 > llin net cards 200201 123 456 78 
           8005551214 < Received report for LLIN net cards: settlements=123, people=456, distributed=78, location=ALBASU CENTRAL
           8005551214 > llin net cards 200201 123 456  
           8005551214 < Invalid form.  The following fields are required: coupons
         """
         
    testUnregisteredSubmissions = """
            tus_1 > llin net cards 200201 123 456 78
            tus_1 < Received report for LLIN net cards: settlements=123, people=456, distributed=78, location=ALBASU CENTRAL. Please register your phone
            tus_1 > llin my status
            tus_1 < Sorry, I don't know who you are.
            tus_2 > llin nets 2001 123 456 78 90
            tus_2 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90. Please register your phone
            tus_2 > llin my status
            tus_2 < Sorry, I don't know who you are.
         """
           
         
    
    def _testKanoLocations(self):
        loc_types = LocationType.objects.all()
        self.assertEqual(6, len(loc_types))
        state = LocationType.objects.get(name="State")
        lga = LocationType.objects.get(name="LGA")
        ward = LocationType.objects.get(name="Ward")
        locations = Location.objects.all()
        # 529 total locations - except we added some others so don't bother
        #self.assertEqual(529, len(locations))
        # 1 state
        self.assertEqual(1, len(locations.filter(type=state)))
        # 44 lgas
        self.assertEqual(44, len(locations.filter(type=lga)))
        # 484 wards
        self.assertEqual(484, len(locations.filter(type=ward)))
        kano = locations.get(type=state)
        self.assertEqual("KANO", kano.name)
        
        self.assertEqual(44, len(kano.children.all()))
        
        for lga in locations.filter(type=lga):
            self.assertEqual(kano, lga.parent)
        
        
    def _testForms(self):
        forms = Form.objects.all()
        self.assertEqual(5, len(forms))
        for form_name in ["register", "issue", "receive", "nets", "net"]:
            # this will throw an error if it doesn't exist
            Form.objects.get(type=form_name)
        
    def _testRoles(self):
        # add this when we have a fixture for roles
        roles = Role.objects.all()
        self.assertEqual(4, len(roles))
        for role_name in ["LGA focal person", "Ward supervisor", "Stock manager", "Distribution point team leader"]:
            # this will throw an error if it doesn't exist
            Role.objects.get(name=role_name)
        