from six import string_types
from django import forms

from rapidsms.backends.http.forms import BaseHttpForm


class KannelForm(BaseHttpForm):
    text = forms.CharField()
    id = forms.CharField()
    charset = forms.CharField(required=False)
    coding = forms.CharField(required=False)

    def clean_text(self):
        # UTF-8 (and possible other charsets) will already be decoded, while
        # UTF-16BE will not, so decode them manually here if we don't already
        # have a unicode string
        charset = self.cleaned_data.get('charset', None)
        text = self.cleaned_data['text']
        if charset and not isinstance(text, string_types):
            text = text.decode(charset)
        return text

    def get_incoming_data(self):
        connections = self.lookup_connections([self.cleaned_data['id']])
        return {'connection': connections[0],
                'text': self.cleaned_data['text']}
