from rapidsms.tests.scripted import TestScript
from form.models import *
from reporters.models import *
import reporters.app as reporter_app
import supply.app as supply_app
import form.app as form_app
import default.app as default_app
from app import App
from django.core.management.commands.dumpdata import Command
import time
import random
import os        
from datetime import datetime

class TestApp (TestScript):
    #apps = (reporter_app.App, App,form_app.App, supply_app.App, default_app.App )
    apps = (reporter_app.App, App,form_app.App, supply_app.App )
    # the test_backend script does the loading of the dummy backend that allows reporters
    # to work properly in tests
    fixtures = ['nigeria_llin', 'test_kano_locations', 'test_backend']
    
    def setUp(self):
        TestScript.setUp(self)
        
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
           8005551212 < Please register your phone with RapidSMS.
           8005551212 > llin register 20 dl dummy user
           8005551212 < Hello dummy! You are now registered as Distribution point team leader at KANO State.
           8005551212 > llin my status
           8005551212 < I think you are dummy user.
           #duplicate submission
           test_reg_dup > llin register 20 dl duplicate user
           test_reg_dup < Hello duplicate! You are now registered as Distribution point team leader at KANO State.
           # this one should be a duplicate
           test_reg_dup > llin register 20 dl duplicate user
           test_reg_dup < Hello again duplicate!  You are already registered as a Distribution point team leader at KANO State.
           # but all of these should create a new registration
           test_reg_dup > llin register 20 dl duplicate user withanothername
           test_reg_dup < Hello duplicate! You are now registered as Distribution point team leader at KANO State.
           test_reg_dup > llin register 20 dl duplicate userlonger
           test_reg_dup < Hello duplicate! You are now registered as Distribution point team leader at KANO State.
           test_reg_dup > llin register 20 dl duplicated user
           test_reg_dup < Hello duplicated! You are now registered as Distribution point team leader at KANO State.
           test_reg_dup > llin register 20 sm duplicate user
           test_reg_dup < Hello duplicate! You are now registered as Stock manager at KANO State.
           test_reg_dup > llin register 2001 dl duplicate user
           test_reg_dup < Hello duplicate! You are now registered as Distribution point team leader at AJINGI LGA.
           # case sensitivity
           test_reg_2 > llin REGISTER 20 dl another user
           test_reg_2 < Hello another! You are now registered as Distribution point team leader at KANO State.
           # different name formats
           test_reg_3 > llin register 20 dl onename
           test_reg_3 < Hello onename! You are now registered as Distribution point team leader at KANO State.
           # these fail
           test_reg_4 > llin register 20 dl mister three names
           test_reg_4 < Hello mister! You are now registered as Distribution point team leader at KANO State.
           test_reg_5 > llin register 20 dl mister four name guy
           test_reg_5 < Hello mister! You are now registered as Distribution point team leader at KANO State.
           # some other spellings
           test_reg_short > llin regstr 20 dl short user
           test_reg_short < Hello short! You are now registered as Distribution point team leader at KANO State.
           test_reg_short_2 > llin regs 20 dl short user
           test_reg_short_2 < Hello short! You are now registered as Distribution point team leader at KANO State.
           test_reg_short_3 > llin reg 20 dl short user
           test_reg_short_3 < Hello short! You are now registered as Distribution point team leader at KANO State.
           test_reg_long > llin registered 20 dl long user
           test_reg_long < Hello long! You are now registered as Distribution point team leader at KANO State.
           # extra spaces
           test_reg_8 > llin    register   20   dl    space     guy
           test_reg_8 < Hello space! You are now registered as Distribution point team leader at KANO State.
           # new tests for more flexible roles
           test_reg_dl > llin register 20 dl distribution leader
           test_reg_dl < Hello distribution! You are now registered as Distribution point team leader at KANO State.
           test_reg_dl_2 > llin register 20 ds distribution leader
           test_reg_dl_2 < Hello distribution! You are now registered as Distribution point team leader at KANO State.
           test_reg_dl_3 > llin register 20 dm distribution leader
           test_reg_dl_3 < Hello distribution! You are now registered as Distribution point team leader at KANO State.
           test_reg_dl_4 > llin register 20 dp distribution leader
           test_reg_dl_4 < Hello distribution! You are now registered as Distribution point team leader at KANO State.
           test_reg_lf > llin register 20 lf lga focal person
           test_reg_lf < Hello lga! You are now registered as LGA focal person at KANO State.
           test_reg_lf > llin register 20 lp lga focal person
           test_reg_lf < Hello again lga!  You are already registered as a LGA focal person at KANO State.
           # alas, we're not perfect
           test_reg_fail > llin rgstr 20 dl sorry guy
           test_reg_fail < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE
         """
    
    testRegistrationErrors = """
           12345 > llin my status
           12345 < Please register your phone with RapidSMS.
           12345 > llin register 45 DL hello world 
           12345 < Invalid form. 45 not in list of location codes
           12345 > llin my status
           12345 < Please register your phone with RapidSMS.
           12345 > llin register 20 pp hello world 
           12345 < Invalid form. Unknown role code: pp
           12345 > llin my status
           12345 < Please register your phone with RapidSMS.
           12345 > llin register 6803 AL hello world 
           12345 < Invalid form. 6803 not in list of location codes. Unknown role code: AL
           12345 > llin my status
           12345 < Please register your phone with RapidSMS.
         """
    
    testKeyword= """
           tkw_1 > llin register 20 dl keyword tester
           tkw_1 < Hello keyword! You are now registered as Distribution point team leader at KANO State.
           # base case
           tkw_1 > llin nets 2001 123 456 78 90
           tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # capitalize the domain
           tkw_1 > LLIN nets 2001 123 456 78 90
           tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # drop an L
           tkw_1 > lin nets 2001 123 456 78 90
           tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # mix the order - this is no longer supported
           #tkw_1 > ILLn nets 2001 123 456 78 90
           #tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           #tkw_1 > ilin nets 2001 123 456 78 90
           #tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # ll anything works?
           tkw_1 > ll nets 2001 123 456 78 90
           tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           tkw_1 > llan nets 2001 123 456 78 90
           tkw_1 < Thank you keyword. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # don't support w/o keyword
           tkw_1 > nets 2001 123 456 78 90
           # the default app to the rescue!
           tkw_1 < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE
        """
    
    testNets= """
           8005551213 > llin register 2001 lf net guy
           8005551213 < Hello net! You are now registered as LGA focal person at AJINGI LGA.
           8005551213 > llin nets 2001 123 456 78 90
           8005551213 < Thank you net. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           8005551213 > llin nets 2001 123 456 78 
           8005551213 < Invalid form. The following fields are required: discrepancy
           # test some of the different form prefix options
           # case sensitivity
           8005551213 > llin NETS 2001 123 456 78 90
           8005551213 < Thank you net. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # no s
           8005551213 > llin net 2001 123 456 78 90
           8005551213 < Thank you net. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # really?  this works?
           8005551213 > llin Nt 2001 123 456 78 90
           8005551213 < Thank you net. Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90
           # something's gotta fail
           8005551213 > llin n 2001 123 456 78 90
           8005551213 < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE
           8005551213 > llin bednets 2001 123 456 78 90
           8005551213 < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE
           8005551213 > llin ents 2001 123 456 78 90
           8005551213 < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE

         """
    
    testNetCards= """
           8005551214 > llin register 200201 lf card guy
           8005551214 < Hello card! You are now registered as LGA focal person at ALBASU CENTRAL Ward.
           8005551214 > llin net cards 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           8005551214 > llin net cards 200201 123 456  
           8005551214 < Invalid form. The following fields are required: issued
           # test some of the different form prefix options
           # case sensitivity
           8005551214 > llin NET CARDS 200201 123 456 78
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           # no s 
           8005551214 > llin net card 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           # one word
           8005551214 > llin netcards 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           8005551214 > llin netcard 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           # he he
           8005551214 > llin nt cd 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           8005551214 > llin ntcrds 200201 123 456 78 
           8005551214 < Thank you card. Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78
           # something's gotta fail
           8005551214 > llin cards 200201 123 456 78 
           8005551214 < Sorry we didn't understand that. Available forms are LLIN: REGISTER, NETCARDS, NETS, RECEIVE, ISSUE
           
         """
         
    testUnregisteredSubmissions = """
            tus_1 > llin net cards 200201 123 456 78
            tus_1 < Received report for LLIN NET CARDS: location=ALBASU CENTRAL, settlements=123, people=456, distributed=78. Please register your phone
            tus_1 > llin my status
            tus_1 < Please register your phone with RapidSMS. 
            tus_2 > llin nets 2001 123 456 78 90
            tus_2 < Received report for LLIN NETS: location=AJINGI, distributed=123, expected=456, actual=78, discrepancy=90. Please register your phone
            tus_2 > llin my status
            tus_2 < Please register your phone with RapidSMS. 
         """
           
    def testGenerateNetFixtures(self): 
        """ This isn't actually a test.  It just takes advantage
            of the test harness to spam a bunch of messages to the 
            nigeria app and spit out the data in a format that can
            be sucked into a fixture.  It should be moved to some 
            data generator at some point, but is being left here 
            for laziness sake """
        # this is the number of net reports that will be generated
        count = 0
        
        # the sender will always be the same, for now
        phone = "55555"
        
        expected_actual_match_percent = .8
        
        
        # allow specifying the minimum and maximum dates for message generation
        min_date = datetime(2009,4,1)
        max_date = datetime(2009,4,30)
        min_time = time.mktime(min_date.timetuple())
        max_time = time.mktime(max_date.timetuple())
        
        # these are the locations that will be chosen.  The actual
        # location will be a distribution point under one of these 
        # wards
        wards = [200101, 200102, 200103, 200104, 200105, 200106, 200107, 200108, 200109, 200110, 200201]
        all_net_strings = []
        for i in range(count):
            # this first part generates a net form at a random DP
            date = datetime.fromtimestamp(random.randint(min_time, max_time))
            ward = Location.objects.get(code=random.choice(wards))
            dp = random.choice(ward.children.all())
            distributed = random.randint(50,500)
            expected = random.randint(0,2000)
            # create an actual amount based on the likelihood of match
            if random.random() < expected_actual_match_percent:
                actual = expected
            else:
                actual = random.randint(0,2000)
            discrepancy = random.randint(0,distributed/5)
            net_string = "%s@%s > llin nets %s %s %s %s %s" % (phone, date.strftime("%Y%m%d%H%M"), dp.code, distributed, expected, actual, discrepancy)
            all_net_strings.append(net_string)
            # the second part generates a net card form at a random MT
            date = datetime.fromtimestamp(random.randint(min_time, max_time))
            ward = Location.objects.get(code=random.choice(wards))
            dp = random.choice(ward.children.all())
            mt = random.choice(dp.children.all())
            settlements = random.randint(3, 50)
            people = random.randint(50, 600)
            coupons = random.randint(50, 600)
            net_card_string = "%s@%s > llin net cards %s %s %s %s" % (phone, date.strftime("%Y%m%d%H%M"), mt.code, settlements, people, coupons )
            all_net_strings.append(net_card_string)
            
        script = "\n".join(all_net_strings)
        self.runScript(script)
        dumpdata = Command()
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__),"fixtures/test_net_data.json"))
        options = { "indent" : 2 }
        datadump = dumpdata.handle("nigeria", **options)
        # uncomment these lines to save the fixture
#        file = open(filename, "w")
#        file.write(datadump)
#        file.close()
#        print "=== Successfully wrote fixtures to %s ===" % filename
#        
    
    def _testKanoLocations(self):
        #TODO test for DPs and MTs
        loc_types = LocationType.objects.all()
        self.assertEqual(6, len(loc_types))
        state = LocationType.objects.get(name="State")
        lga = LocationType.objects.get(name="LGA")
        ward = LocationType.objects.get(name="Ward")
        locations = Location.objects.all()
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
        for form_name in ["register", "issue", "receive", "nets", "netcards"]:
            # this will throw an error if it doesn't exist
            Form.objects.get(code__abbreviation=form_name)
        
    def _testRoles(self):
        # add this when we have a fixture for roles
        roles = Role.objects.all()
        self.assertEqual(4, len(roles))
        for role_name in ["LGA focal person", "Ward supervisor", "Stock manager", "Distribution point team leader"]:
            # this will throw an error if it doesn't exist
            Role.objects.get(name=role_name)
        
