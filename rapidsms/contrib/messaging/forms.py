#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms

from rapidsms.router import send

from selectable.forms import AutoCompleteSelectMultipleField

from .lookups import ContactLookup


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    recipients = AutoCompleteSelectMultipleField(lookup_class=ContactLookup)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['recipients'].widget.attrs['placeholder'] = 'Add a Contact'
        self.fields['message'].widget.attrs['placeholder'] = 'Message'

    def send(self):
        connections = []
        for recipient in self.cleaned_data['recipients']:
            connections.append(recipient.default_connection)
        send(self.cleaned_data['message'], connections)
        return self.cleaned_data['message'], self.cleaned_data['recipients']
