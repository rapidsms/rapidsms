#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from rapidsms.models import Contact, Connection


class ConnectionFormSetBase(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(ConnectionFormSetBase, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False
        self.forms[0].fields['DELETE'].widget = forms.widgets.HiddenInput()


ContactForm = forms.models.modelform_factory(Contact, exclude=("connections", ))

ConnectionFormSet = forms.models.inlineformset_factory(
    Contact,
    Connection,
    extra=1,
    max_num=10,
    formset=ConnectionFormSetBase,
)


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
