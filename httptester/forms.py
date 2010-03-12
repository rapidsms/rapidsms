#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import forms


class MessageForm(forms.Form):
    identity = forms.CharField(
        label="Phone Number",
        max_length=100,
        help_text="The phone number which this message will appear " +\
                  "to have originated from.")

    text = forms.CharField(
        label="Message Text",
        required=False,
        widget=forms.widgets.Textarea({
            "cols": 30,
            "rows": 6 }))
