# -*- coding: utf-8 -*-
from rapidsms.tests.scripted import TestScript
from django.core.management import call_command
from django.test import TestCase

from app import App

from models.logs import MessageLog, EventLog
from models.general import Provider, User, Facility
from models.general import Case, CaseNote
from models.reports import ReportMalnutrition, ReportMalaria, Observation, Diagnosis

from datetime import datetime, date, timedelta

def age_in_months (*ymd):
    return int((datetime.now().date() - date(*ymd)).days / 30.4375)    

def age_in_years (*ymd):
    return int((datetime.now().date() - date(*ymd)).days / 365.25)

def date_boundaries():
    now = datetime.now()
    mapping = {
        "under 2 months": 45,
        "over 2 months": 72,
        "over 1 year": 380,
        "over 2 years": 770,
        "over 3 years": 1110,
        "over 6 years": 2300,
        "over 9 years": 3300,
        "over 15 years": 5500
    }
    for age, diff in mapping.items():
        mapping[age] = (now - timedelta(days=diff)).strftime("%d%m%Y")

    return mapping

loaded = False
class TestApp (TestScript):
    fixtures = ('test.json', 'observations.json', 'lab_codes.json', 'diagnoses.json', 'diagnoses_categories.json')
    apps = (App,)
    
    def setUp (self):
        # since the database is not nuked, there's no point in reloading these every time
        # this also messes up 13 and 14 which change the db
        # plus the unit tests are waaaay faster
        global loaded
        if not loaded:
            # borrowed from django/test/testcases.py
            call_command('loaddata', *self.fixtures, **{'verbosity': 0})            
            loaded = True
        TestScript.setUp(self)

    test_00_Join = """
        # test registration
        1234567 > join pear smith ken
        1234567 < The given password is not recognized.

        # test registration
        1234567 > join apple smith ken
        1234567 < 1234567 registered to @ksmith (SMITH, Ken) at Alphaville.

        # test re-registration
        1234567 > join apple smith ken
        1234567 < Username 'ksmith' is already in use. Reply with: JOIN <last> <first> <username>

        # username lookup is case insensitive
        1234567 > join apple smith ken KSMITH
        1234567 < Username 'ksmith' is already in use. Reply with: JOIN <last> <first> <username>
 
        # test takeover/confirm
        1234567 > join banana smith ken smithk
        1234567 < Phone 1234567 is already registered to SMITH, Ken. Reply with 'CONFIRM smithk'.   
        1234567 > confirm smithk
        1234567 < 1234567 registered to @smithk (SMITH, Ken) at Bravo Town.
    """

    test_00_MessageLog_1 = """
        # this should provoke no response at all
        7654321 > *yawn*
    """

    def test_00_MessageLog_2 (self):
        msgs = MessageLog.objects.count()
        self.assertEqual(7, msgs, "message log count is %d" % msgs)
        msgs = MessageLog.objects.filter(was_handled=True).count()
        self.assertEqual(6, msgs, "handled message count is %d" % msgs)

    test_01_DirectMessage = """
        # test authentication
        7654321 > @2 can you read this?
        7654321 < 7654321 is not a registered number.

        # test direct messaging
        7654321 > join cherry doe jane
        7654321 < 7654321 registered to @jdoe (DOE, Jane) at Charliesburg.
        7654321 > @6 can you read this? 
        1234567 < @jdoe> can you read this?
        1234567 > @jdoe yes, I can read that
        7654321 < @smithk> yes, I can read that
        7654321 > @SMITHK GOOD THANKS
        1234567 < @jdoe> GOOD THANKS

        # test direct messaging to a non-existent user
        7654321 > @14 are you there?
        7654321 < User @14 is not registered.
        7654321 > @kdoe are you there?
        7654321 < User @kdoe is not registered.

        # FIXME: what happens if you message an inactive provider???
    """

    caseAges = (
        age_in_months(2008,4,11),
        age_in_years(2005,4,11),
        age_in_months(2009,2,11),
        age_in_months(2007,6,15),)
    
    test_01_NewCase = """
        # test basic case creation
        7654321 > new madison dolly f 110408
        7654321 < New +18: MADISON, Dolly F/%dm (None) Whiskey

        # case with guardian and age in years
        7654321 > new madison molly f 110405 sally
        7654321 < New +26: MADISON, Molly F/%d (Sally) Whiskey

        # case with guardian and phone number
        7654321 > new madison holly f 110209 sally 230123
        7654321 < New +34: MADISON, Holly F/%dm (Sally) Whiskey

        # case with phone number but no guardian
        7654321 > new madison wally m 150607 230123
        7654321 < New +42: MADISON, Wally M/%dm (None) Whiskey

        # FIXME: unparsable cases???
    """ % caseAges

    def test_02_CreatedCases(self):        
        user = User.objects.get(username="jdoe")
        case = Case.objects.get(ref_id=42)
        self.assertEqual(case.mobile, "230123", "case 42 mobile")
        self.assertEqual(case.provider, user.provider, "case 42 provider")

        case = Case.objects.get(ref_id=34)
        self.assertEqual(case.mobile, "230123", "case 34 mobile")
        self.assertEqual(case.guardian, "Sally", "case 34 guardian")
        self.assertEqual(case.provider, user.provider, "case 34 provider")

    test_02_ListCases = """
        0000000 > list
        0000000 < 0000000 is not a registered number.

        7654321 > list
        7654321 < +18 MADISON D. F/%dm, +26 MADISON M. F/%d, +34 MADISON H. F/%dm, +42 MADISON W. M/%dm
    """ % caseAges

    test_02_ListProviders = """
        0000000 > list @
        0000000 < 0000000 is not a registered number.

        7654321 > list @
        7654321 < @1 admin, @2 staff, @3 nonstaff, @4 nonactive, @5 ksmith, @6 smithk, @7 jdoe
    """
    
    test_03_CancelCases = """
        0000000 > cancel +34
        0000000 < 0000000 is not a registered number.
        
        7654321 > cancel +34
        7654321 < Case +34 cancelled.
        7654321 > cancel 42
        7654321 < Case +42 cancelled. 
        7654321 > cancel 42
        7654321 < Case +42 not found. 
    """ 

    test_03_ReportCase = """
        # authenticated
        0000000 > muac +26 7.5 e
        0000000 < 0000000 is not a registered number.
        
        # basic test
        7654321 > muac +26 75 n
        7654321 < MUAC> SAM Patient requires OTP care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm

        # cm get converted to mm, g to kg, m to cm
        7654321 > muac +26 7.5 2150 1.4 n
        7654321 < MUAC> SAM Patient requires OTP care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, 2.1 kg, 140 cm

        # complications list
        7654321 > muac +26 75 21 e a d
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, 21.0 kg, Appetite Loss, Diarrhea, Edema

        # complications list - weight is optional
        7654321 > muac +26 75 e a d
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, Appetite Loss, Diarrhea, Edema

        # complications list - case insensitive
        7654321 > MUAC +26 75 21 N A D
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, 21.0 kg, Appetite Loss, Diarrhea

        # more complications, formatted differently
        7654321 > muac +26 75 n fcv
        7654321 < Unknown observation code: fcv

        # more complications, formatted differently
        7654321 > muac +26 75 n f cg v
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, Coughing, Fever, Vomiting


        # one last complication test
        7654321 > muac +26 75 21 n u
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 75 mm, 21.0 kg, Unresponsive

        # MAM logic test
        7654321 > muac +26 120 n
        7654321 <  MUAC> MAM Child requires supplemental feeding.. +26 MADISON, M, F/4 (Sally). MUAC 120 mm

        # Healthy logic test
        7654321 > muac +26 125 n
        7654321 <  MUAC> Child is not malnourished. +26 MADISON, M, F/4 (Sally). MUAC 125 mm

        # MUAC fail
        7654321 > muac +26 45.5.5 83.1 e foo
        7654321 < Can't understand MUAC (mm): 45.5.5

        # weight fail
        7654321 > muac +26 45 83.1.1 e foo
        7654321 < Can't understand weight (kg): 83.1.1

        # height fail
        7654321 > muac +26 45 83.1 122.1.1 e foo
        7654321 < Can't understand height (cm): 122.1.1

        # complication fail
        7654321 > muac +26 800 N MUST RECEIVE HELP
        7654321 < Unknown observation code: must
    """

    def test_03_ReportOverwrite (self):
        reports = Case.objects.get(ref_id=26).reportmalnutrition_set.count()

        self.assertEquals(reports, 1,
            "only have one report; all others today were overwritten")

    _test_03_ShowCase = """
        7654321 > show +26
        7654321 < +26 Healthy MADISON, Molly F/4 (Sally) Whiskey
    """
    
    test_04_NoteCase_1 = """
        # authenticated
        0000000 > n +26 how are you gentleman! all your base are belong to us
        0000000 < 0000000 is not a registered number.
        
        # add a case note
        7654321 > n +26 child seems to be recovering.
        7654321 < Note added to case +26.

        # this syntax works too
        7654321 > note +26 will check back tomorrow
        7654321 < Note added to case +26.
    """

    def test_04_NoteCase_2 (self):
        notes = Case.objects.get(ref_id=26).notes.count()
        self.assertEqual(notes, 2, "have %d notes about +26" % notes)

    def test_zzz_queue_is_empty (self):
        self.assertFalse(self.backend.message_waiting)

    test_05_Fever = """
        # requested change to make f be fever, not h
        7654321 > muac +26 105 d v f
        7654321 < MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 105 mm, Diarrhea, Fever, Vomiting
    """
    
    test_06_Lists = """
        # test of mulitiple recipients and report of a case
        7654322 > join cherry bob smith
        7654322 < 7654322 registered to @sbob (BOB, Smith) at Charliesburg.
        
        7654321 > muac +26 105 d v f
        7654321 <  MUAC> SAM+ Patient requires IMMEDIATE inpatient care. +26 MADISON, M, F/4 (Sally). MUAC 105 mm, Diarrhea, Fever, Vomiting
        # 7654322 < @jdoe reports +26: SAM+, MUAC 105 mm, Diarrhea, Fever, Vomiting
    """

    def test_07_mrdt_00(self):
        first = User.objects.get(username="jdoe").provider
        second = User.objects.get(username="sbob").provider
        second.following_users.add(first)
        second.alerts = True
        second.save()

    test_07_mrdt_01 = """
        7654321 > mrdt +234 n y a
        7654321 < Case +234 not found.
        
        7654321 > mrdt +26 y n f
        7654321 < MRDT> Child +26, MADISON, Molly, F/4 has MALARIA. Child is 4. Please provide 2 tabs of Coartem (ACT) twice a day for 3 days
        7654322 < MRDT> Child +26, MADISON, Molly, F/4 (None) has MALARIA. CHW: @jdoe 7654321
        
        7654321 > mrdt +26 n y f e
        7654321 < MRDT> Child +26, MADISON, Molly, F/4 (Sally), None. RDT=N, Bednet=Y, (Edema, Fever). Please refer patient IMMEDIATELY for clinical evaluation
        7654322 < MRDT> Negative MRDT with Fever. +26, MADISON, Molly, F/4 None. Patient requires IMMEDIATE referral. Reported by CHW J DOE @jdoe m:7654321.
        
        7654321 > mrdt +26 n y fe
        7654321 < Unknown observation code: fe
        
        7654321 > mrdt +26 n n
        7654321 < MRDT> Child +26, MADISON, Molly, F/4 (Sally), None. RDT=N, Bednet=N. Please refer patient IMMEDIATELY for clinical evaluation   
        7654322 < MRDT> Negative MRDT with Fever. +26, MADISON, Molly, F/4 None. Patient requires IMMEDIATE referral. Reported by CHW J DOE @jdoe m:7654321.

        7654321 > mrdt +26 n n q
        7654321 < Unknown observation code: q     
        
        7654321 > new madison molly f %s emily
        7654321 < New +34: MADISON, Molly F/12m (Emily) Whiskey

        7654321 > mrdt +34 y n f
        7654321 < MRDT> Child +34, MADISON, Molly, F/12m has MALARIA. Child is less than 3. Please provide 1 tab of Coartem (ACT) twice a day for 3 days
        7654322 < MRDT> Child +34, MADISON, Molly, F/12m (None) has MALARIA. CHW: @jdoe 7654321

        7654321 > mrdt +34 y n
        7654321 < MRDT> Child +34, MADISON, Molly, F/12m has MALARIA. Child is less than 3. Please provide 1 tab of Coartem (ACT) twice a day for 3 days
        7654322 < MRDT> Child +34, MADISON, Molly, F/12m (None) has MALARIA. CHW: @jdoe 7654321

        7654321 > new madison foo f %s emily
        7654321 < New +42: MADISON, Foo F/3 (Emily) Whiskey

        7654321 > mrdt +42 y n cf e
        7654321 < MRDT> Child +42, MADISON, Foo, F/3 has MALARIA and danger signs (Confusion). Refer to clinic immediately after 2 tabs of Coartem is given
        7654322 < MRDT> Child +42, MADISON, Foo, F/3 (None) has MALARIA and danger signs (Confusion). CHW: @jdoe 7654321
        
        
        7654321 > mrdt +42 y n e
        7654321 < MRDT> Child +42, MADISON, Foo, F/3 has MALARIA. Child is 3. Please provide 2 tabs of Coartem (ACT) twice a day for 3 days
        7654322 < MRDT> Child +42, MADISON, Foo, F/3 (None) has MALARIA. CHW: @jdoe 7654321

        7654321 > new madison sam f %s samantha
        7654321 < New +59: MADISON, Sam F/2m (Samantha) Whiskey

        7654321 > mrdt +59 y n cf e
        7654321 < MRDT> Child +59, MADISON, Sam, F/2m has MALARIA and danger signs (Confusion). Refer to clinic immediately after 1 tab of Coartem is given
        7654322 < MRDT> Child +59, MADISON, Sam, F/2m (None) has MALARIA and danger signs (Confusion). CHW: @jdoe 7654321
        

        7654321 > mrdt +59 n n cf e
        7654321 < MRDT> Child +59, MADISON, Sam, F/2m (Samantha), None. RDT=N, Bednet=N, (Confusion, Edema). Please refer patient IMMEDIATELY for clinical evaluation
        7654322 < MRDT> Negative MRDT with Fever. +59, MADISON, Sam, F/2m None. Patient requires IMMEDIATE referral. Reported by CHW J DOE @jdoe m:7654321.
    """ % (date_boundaries()["over 1 year"], date_boundaries()["over 3 years"], date_boundaries()["over 2 months"])
        

    def test_07_mrdt_02(self):
        # like malnutrition, this nukes any other report on the same day
        # in the previous test, 3 reports were sent in
        reports = Case.objects.get(ref_id=26).reportmalaria_set.all()
        assert len(reports) == 1
        assert not len(reports[0].observed.all())

    test_08_diagnosis = """ 
        7654321 > D +234 Hey ho!
        7654321 < Case +234 not found.
    
        7654321 > D +59 -000.00
        7654321 < Unknown diagnosis code: 000.00

        7654321 > D +59 -084.9
        7654321 < D> +59 S.MADISON C. Malaria

        7654321 > D +59 -084.9 -480
        7654321 < D> +59 S.MADISON C. Malaria, Viral Pneumonia

        7654321 > D +59 /foo+
        7654321 < Unknown lab code: /foo

        7654321 > D +59 /ElISA+ /rdt- /BS+45
        7654321 < D> +59 S.MADISON Labs: ELISA+, RDT-, BS 45

        7654321 > D +59 Looked ill /HB+10 had -084.9 and -480 and so on /ELISA-
        7654321 < D> +59 S.MADISON C. Malaria, Viral Pneumonia Labs: HB 10, ELISA-
    """

    # lets test some nice error cases re handled
    test_09_errors = """
        7654321 > foo!
        7654321 < Unknown or incorrectly formed command: foo!... Please call 999-9999
    """
    
    test_10_zones = """
        7654321 > new madison wally m 150607 230123
        7654321 < New +67: MADISON, Wally M/%dm (None) Whiskey

        7654321 > new madison wally m 150607 230123 z1
        7654321 < New +75: MADISON, Wally M/%dm (None) X-Ray

        7654321 > new madison wally m 150607 z1
        7654321 < New +83: MADISON, Wally M/%dm (None) X-Ray
    """ % (caseAges[-1], caseAges[-1], caseAges[-1])
    
    test_11_cancel_fails = """
        7654321 > new JAMES Davey m 150607 230123
        7654321 < New +91: JAMES, Davey M/%dm (None) Whiskey
        
        7654321 > D +91 -084.9
        7654321 < D> +91 D.JAMES C. Malaria
        
        7654321 > cancel +91
        7654321 < Cannot cancel +91: case has diagnosis reports.

        7654321 > new james billy m 150607 230123
        7654321 < New +108: JAMES, Billy M/%dm (None) Whiskey
        
        7654321 > mrdt +108 y n f
        7654321 < MRDT> Child +108, JAMES, Billy, M/22m has MALARIA. Child is less than 3. Please provide 1 tab of Coartem (ACT) twice a day for 3 days
        7654322 < MRDT> Child +108, JAMES, Billy, M/22m (None) has MALARIA. CHW: @jdoe 7654321
        
        7654321 > cancel +108
        7654321 < Cannot cancel +108: case has malaria reports.        
    """ % (caseAges[-1], caseAges[-1])

#    test_12_utf = """
#        7654321 > D +91 -084.9 Vaqif Səmədoğl
#        7654321 < D> +91 D.JAMES C. Malaria
#    """

    def test_13_diagnosis(self):
        """ Just a setup for the next bit """
        d = Diagnosis.objects.get(id=4)
        d.instructions = "Some test instructions"
        d.save()

    test_14_diagnosis = """
        7654322 > D +91 -002
        7654322 < D> +91 D.JAMES Typhoid        

        7654322 > D +91 -001 
        7654322 < D> +91 D.JAMES Cholera
        7654321 < D> +91 Some test instructions
    """

class TestAlerts(TestCase):
    fixtures = ["users.json", "alerts.json"]

    def testCreateReport(self):
        provider = Provider.objects.get(id=2)
        clinic = provider.clinic

        report = ReportMalaria()
        report.provider = provider
        recipients = report.get_alert_recipients()
        assert len(recipients) == 3, [ r.id for r in recipients ]

        one = Provider.objects.get(id=1)
        one.alerts = False
        one.save()

        recipients = report.get_alert_recipients()
        assert len(recipients) == 2

        one = Provider.objects.get(id=1)
        one.alerts = True
        one.save()

        recipients = report.get_alert_recipients()
        assert len(recipients) == 3

        four = Provider.objects.get(id=4)
        four.following_users.remove(provider)
        four.save()

        recipients = report.get_alert_recipients()
        assert len(recipients) == 2

        one.following_clinics.remove(clinic)
        one.save()

        recipients = report.get_alert_recipients()        
        assert len(recipients) == 1, [ r.id for r in recipients ]        
