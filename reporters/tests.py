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
        edge_type = EdgeType(name="Location Parent", parent_type=loc_type, child_type=loc_type)
        edge_type.save()
        state = Location(name="Kano")
        state.save()
        lga = Location(name="Kano LGA")
        lga.parent=state
        lga.save()
        edge = Edge.objects.get(relationship=edge_type, child_id =lga.id)
        self.assertTrue(edge)
        self.assertEqual(edge.child_object, lga)
        self.assertEqual(edge.parent_object, state)
        lga_back = Location.objects.get(name="Kano LGA")
        self.assertEqual(state, lga.parent)
        