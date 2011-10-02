from django import forms

from rapidsms.router import Router
from rapidsms.models import Contact


class MessageForm(forms.Form):
	text = forms.CharField()
	recipients = forms.ModelMultipleChoiceField(queryset=None)

	def __init__(self, *args, **kwargs):
		super(MessageForm, self).__init__(*args, **kwargs)
		recipients = Contact.objects.filter(connection__isnull=False)
		self.fields['recipients'].queryset = recipients.distinct()

	def send(self):
	    router = Router()
	    for recipient in self.cleaned_data['recipients']:
	        router.handle_outgoing(self.cleaned_data['text'],
	                               connection=recipient.default_connection)
	    return self.cleaned_data['recipients']
