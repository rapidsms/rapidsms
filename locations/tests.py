#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.test import TestCase
from .models import Location


class LocationTest(TestCase):
    def testSlug(self):

        rest = Location.objects.create(name="Garret's", slug="grt")
        self.assertEqual("grt", rest.slug, "Slug field was not what was expected!")

        rest = Location.objects.create(name="Portico", slug=" pr t   ")
        self.assertEqual("pr t", rest.slug, "Spaces were not truncated from slug!")

        rest = Location.objects.create(name="Diane's", slug="DIA")
        self.assertEqual("dia", rest.slug, "Slug was not converted to lowercase!")
