from django import forms

from rapidsms.backends.http.forms import BaseHttpForm


class VumiForm(BaseHttpForm):
    message_id = forms.CharField()
    to_addr = forms.CharField()
    from_addr = forms.CharField()
    in_reply_to = forms.CharField(required=False)
    session_event = forms.CharField()
    content = forms.CharField()
    transport_name = forms.CharField()
    transport_type = forms.CharField()
    group = forms.CharField(required=False)

    def get_incoming_data(self):
        fields = self.cleaned_data.copy()
        return {'identity': self.cleaned_data['from_addr'],
                'text': self.cleaned_data['content'],
                'fields': fields}
