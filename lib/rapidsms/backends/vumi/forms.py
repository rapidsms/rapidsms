from django import forms

from rapidsms.backends.http.forms import BaseHttpForm


class VumiForm(BaseHttpForm):
    content = forms.CharField()
    from_adr = forms.CharField()
    to_adr = forms.CharField(required=False)
    message_id = forms.CharField(required=False)

    def get_incoming_data(self):
        return {'identity': self.cleaned_data['from_adr'],
                'text': self.cleaned_data['content']}
