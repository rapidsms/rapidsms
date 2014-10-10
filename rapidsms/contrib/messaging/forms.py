#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms

from rapidsms.router import send

from selectable.forms import AutoCompleteSelectMultipleField

from .lookups import ConnectionLookup


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    connections = AutoCompleteSelectMultipleField(
        lookup_class=ConnectionLookup)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['connections'].widget.attrs['placeholder'] = 'Add a Recipient'
        self.fields['message'].widget.attrs['placeholder'] = 'Message'

    def send(self):
        message = self.cleaned_data['message']
        connections = self.cleaned_data['connections']
        return send(message, connections)
