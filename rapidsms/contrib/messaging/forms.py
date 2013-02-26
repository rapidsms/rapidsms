from django import forms

from rapidsms.models import Contact
from rapidsms.router import send

from selectable.forms import AutoCompleteSelectMultipleField

from rapidsms.contrib.messaging.lookups import ContactLookup


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    recipients = AutoCompleteSelectMultipleField(lookup_class=ContactLookup)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['recipients'].widget.attrs['placeholder'] = 'Add a Contact'
        self.fields['message'].widget.attrs['placeholder'] = 'Message'

    def send(self):
        for recipient in self.cleaned_data['recipients']:
            send(self.cleaned_data['message'], recipient.default_connection)
        return self.cleaned_data['text'], self.cleaned_data['recipients']
