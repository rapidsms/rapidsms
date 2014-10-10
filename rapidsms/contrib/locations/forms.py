#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.utils.translation import ugettext_lazy as _
from django.forms import fields, widgets
from django import forms

from .models import Location, Point


class PointWidget(widgets.MultiWidget):
    default_attrs = {"size": 6}

    def __init__(self, attrs=None):
        attrs_ = self.default_attrs.copy()
        attrs_.update(attrs or {})

        _widgets = (widgets.TextInput(attrs=attrs_),
                    widgets.TextInput(attrs=attrs_))
        super(PointWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            p = Point.objects.get(pk=value)
            return [p.latitude, p.longitude]

        return [None, None]


class PointField(fields.MultiValueField):
    widget = PointWidget

    default_error_messages = {
        "invalid_lat": _(u"Enter a valid latitude."),
        "invalid_lng": _(u"Enter a valid longitude.")}

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()

        if "error_messages" in kwargs:
            errors.update(kwargs["error_messages"])

        lat_field = fields.FloatField(
            error_messages={"invalid": errors["invalid_lat"]},
            min_value=-90,
            max_value=90)

        lng_field = fields.FloatField(
            error_messages={"invalid": errors["invalid_lng"]},
            min_value=-180,
            max_value=180)

        super(PointField, self).__init__((lat_field, lng_field),
                                         *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            lat = unicode(data_list[0])
            lng = unicode(data_list[1])
            return Point.objects.create(
                latitude=lat, longitude=lng)

        return None


class LocationForm(forms.ModelForm):
    point = PointField(
        label="Coordinates",
        help_text="The physical latitude and longitude of this location.")

    class Meta:
        model = Location
        exclude = ("parent_type", "parent_id", "type")


# class CountryForm(LocationForm):
#    class Meta:
#        model = Country
#        exclude = ("parent_type", "parent_id")


# class StateForm(LocationForm):
#    class Meta:
#        model = State
#        exclude = ("parent_type", "parent_id")


# class CityForm(LocationForm):
#    class Meta:
#        model = City
#        exclude = ("parent_type", "parent_id")
