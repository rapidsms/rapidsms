from rapidsms.tests.scripted import TestScript
from app import App
from models import *
from apps.modelrelationship.models import *
from django.contrib.contenttypes.models import ContentType

    
class TestApp (TestScript):
    apps = (App,)

    
    def setUp(self):
        TestScript.setUp(self)
            

    def testModel(self):
        loc_type = ContentType.objects.get(name="location")
        state = Location(name="Kano")
        state.save()
        lga = Location(name="Kano LGA")
        lga.parent=state
        lga.save()
        lga_back = Location.objects.get(name="Kano LGA")
        self.assertEqual(state, lga_back.parent)
        # also change it and make sure it updates instead of adds
        state2 = Location(name="Abuja")
        state2.save()
        lga_back.parent = state2
        lga_back.save()
        lga_back_again = Location.objects.get(name="Kano LGA")
        self.assertEqual(state2, lga_back_again.parent)
        
