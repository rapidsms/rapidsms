#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from rapidsms.models import Contact, Connection


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ("connections",)

ConnectionFormSet = forms.models.inlineformset_factory(
    Contact,
    Connection,
    extra=1,
    max_num=10)

# the built-in FileField doesn't specify the 'size' attribute, so the
# widget is rendered at its default width -- which is too wide for our
# form. this is a little hack to shrink the field.
class SmallFileField(forms.FileField):
    def widget_attrs(self, widget):
        return {"size": 10}


class BulkRegistrationForm(forms.Form):
    bulk = SmallFileField(
        label="Upload CSV file",
        required=False,
        help_text="Upload a <em>plain text file</em> " +
                  "containing a single contact per line, for example: <br/>" +
                  "<em>firstname lastname, backend_name, identity</em>")
