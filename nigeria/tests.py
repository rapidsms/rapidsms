from rapidsms.tests.scripted import TestScript
from apps.form.models import *
from apps.reporters.models import *
import apps.reporters.app as reporter_app
import apps.supply.app as supply_app
import apps.form.app as form_app
from app import App

class TestApp (TestScript):
    apps = (reporter_app.App, App,form_app.App, supply_app.App )
    fixtures = ['nigeria_llin', 'kano_locations', 'kano_location_parents']
    
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
        
    testRegistration = """
           8005551212 > llin my status
           8005551212 < Sorry, I don't know who you are.
           8005551212 > llin register 20 dl secret dummy user
           8005551212 < Hello duser! You are now registered as Distribution point team leader at KANO State.
           8005551212 > llin my status
           8005551212 < I think you are are dummy user.
         """
    
    testNets= """
           8005551213 > llin nets 2001 123 456 78 90
           8005551213 < Invalid form.  You must register your phone before submitting data
           8005551213 > llin register 2001 lf anothersecret net guy
           8005551213 < Hello nguy! You are now registered as LGA focal person at AJINGI LGA.
           8005551213 > llin nets 2001 123 456 78 90
           8005551213 < Received report for LLIN nets: expected=456, actual=78, location=AJINGI, distributed=123, discrepancy=90
           8005551213 > llin nets 2001 123 456 78 
           8005551213 < Invalid form.  The following fields are required: discrepancy
         """
    
    testNetCards= """
           8005551214 > llin net cards 200201 123 456 78 
           8005551214 < Invalid form.  You must register your phone before submitting data
           8005551214 > llin register 200201 lf anothersecret card guy
           8005551214 < Hello cguy! You are now registered as LGA focal person at ALBASU CENTRAL Ward.
           8005551214 > llin net cards 200201 123 456 78 
           8005551214 < Received report for LLIN net cards: settlements=123, people=456, distributed=78, location=ALBASU CENTRAL
           8005551214 > llin net cards 200201 123 456  
           8005551214 < Invalid form.  The following fields are required: coupons
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
        
        # test edge and edge type generation.  
        # TODO these don't play nice with new db's because the content type
        # id's change.  We need a true workaround for this.
        self.assertEqual(1, len(EdgeType.objects.all()))
        parent_type = EdgeType.objects.all()[0]
        self.assertEqual(528, len(Edge.objects.all()))
        
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
        