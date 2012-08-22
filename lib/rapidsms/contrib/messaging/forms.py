from django import forms

from rapidsms.models import Contact

from rapidsms.messages.router_api import handle_outgoing


class MessageForm(forms.Form):
	text = forms.CharField()
	recipients = forms.ModelMultipleChoiceField(queryset=None)

	def __init__(self, *args, **kwargs):
		super(MessageForm, self).__init__(*args, **kwargs)
		recipients = Contact.objects.filter(connection__isnull=False)
		self.fields['recipients'].queryset = recipients.distinct()

	def send(self):
	    for recipient in self.cleaned_data['recipients']:
	        handle_outgoing(self.cleaned_data['text'],
	                        connection=recipient.default_connection)
	    return self.cleaned_data['recipients']
