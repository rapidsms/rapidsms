from django.test import TestCase
from .models import Location, LocationType
from _mysql_exceptions import IntegrityError

class LocationTest(TestCase):
    
    def setUp(self):
        self.type = LocationType.objects.create\
                (singular="restaurant", plural="restaurants", slug="rest")
        
    def testSlug(self):
        
        rest = Location.objects.create(type=self.type, name="Garret's", slug="grt")
        self.assertEqual("grt", rest.slug, "Slug field was not what was expected!")
        
        rest = Location.objects.create(type=self.type, name="Portico", slug=" pr t   ")
        self.assertEqual("pr t", rest.slug, "Spaces were not truncated from slug!")
        
        rest = Location.objects.create(type=self.type, name="Diane's", slug="DIA")
        self.assertEqual("dia", rest.slug, "Slug was not converted to lowercase!")
        
        Location.objects.create(type=self.type, name="Muskaan", slug="mk")
        try:
            Location.objects.create(type=self.type, name="Muskaan 2", slug=" MK ")
            self.fail("Creating location with a duplicate slug should fail!")
        except IntegrityError:
            pass
        