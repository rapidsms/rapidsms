#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms


# the built-in FileField doesn't specify the 'size' attribute, so the
# widget is rendered at its default width -- which is too wide for our
# form. this is a little hack to shrink the field.
from django.core.exceptions import ValidationError


class SmallFileField(forms.FileField):
    def widget_attrs(self, widget):
        return {"size": 10}


class MessageForm(forms.Form):
    identity = forms.CharField(
        label="Phone Number",
        max_length=100,
        help_text="The phone number which this message " +
                  "will appear to have originated from.")

    text = forms.CharField(
        label="Single Message",
        required=False,
        widget=forms.widgets.Textarea({
            "cols": 30,
            "rows": 4}))

    bulk = SmallFileField(
        label="Multiple Messages",
        required=False,
        help_text="Alternatively, upload a <em>plain text file</em> " +
                  "containing a single message per line.")

    def clean_identity(self):
        if 'identity' in self.cleaned_data:
            identity = self.cleaned_data['identity'].strip()
            if not identity.isnumeric():
                raise ValidationError("Phone number must be all numeric")
            return identity
