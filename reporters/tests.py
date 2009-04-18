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
        edge_type = NewEdgeType(name="Location Parent", parent_type=loc_type, child_type=loc_type)
        edge_type.save()
        state = Location(name="Kano")
        state.save()
        lga = Location(name="Kano LGA")
        lga.parent=state
        lga.save()
        edge = NewEdge.objects.get(relationship=edge_type, child_id =lga.id)
        self.assertTrue(edge)
        self.assertEqual(edge.child_object, lga)
        self.assertEqual(edge.parent_object, state)
        lga_back = Location.objects.get(name="Kano LGA")
        self.assertEqual(state, lga_back.parent)
        # also change it and make sure it updates instead of adds
        state2 = Location(name="Abuja")
        state2.save()
        lga_back.parent = state2
        lga_back.save()
        edges = NewEdge.objects.all().filter(relationship=edge_type).filter(child_id =lga_back.id)
        self.assertEqual(1, len(edges))
        edge = edges[0]
        self.assertEqual(edge.child_object, lga_back)
        self.assertEqual(edge.parent_object, state2)
        lga_back_again = Location.objects.get(name="Kano LGA")
        self.assertEqual(state2, lga_back_again.parent)
        