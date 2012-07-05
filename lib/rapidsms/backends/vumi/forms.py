from django import forms

from rapidsms.backends.http.forms import BaseHttpForm


class VumiForm(BaseHttpForm):
    text = forms.CharField()
    id = forms.CharField()
    message_id = forms.CharField(required=False)

    def get_incoming_data(self):
        return {'identity': self.cleaned_data['id'],
                'text': self.cleaned_data['text']}
