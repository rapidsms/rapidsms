from django import forms

from rapidsms.models import Contact

from rapidsms.router import send


class MessageForm(forms.Form):
    text = forms.CharField()
    recipients = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        recipients = Contact.objects.filter(connection__isnull=False)
        self.fields['recipients'].queryset = recipients.distinct()

    def send(self):
        connections = []
        for recipient in self.cleaned_data['recipients']:
            connections.append(recipient.default_connection)
        send(self.cleaned_data['text'], connections)
        return self.cleaned_data['recipients']
