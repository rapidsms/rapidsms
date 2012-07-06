from django import forms

from rapidsms.backends.http.forms import BaseHttpForm


class VumiForm(BaseHttpForm):
    content = forms.CharField()
    from_addr = forms.CharField()
    to_addr = forms.CharField(required=False)
    message_id = forms.CharField(required=False)

    def get_incoming_data(self):
        return {'identity': self.cleaned_data['from_addr'],
                'text': self.cleaned_data['content']}
