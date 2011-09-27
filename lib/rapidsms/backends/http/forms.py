from django import forms


class BaseHttpForm(forms.Form):

    def get_incoming_data(self):
        raise NotImplementedError()


class GenericHttpForm(BaseHttpForm):

    def __init__(self, *args, **kwargs):
        """
        Saves the identify (phone number) and text field names on self, calls
        super(), and then adds the required fields.
        """
        self.text_name = kwargs.pop('text_name')
        self.identity_name = kwargs.pop('identity_name')
        super(GenericHttpForm, self).__init__(*args, **kwargs)
        self.fields[self.text_name] = forms.CharField()
        self.fields[self.identity_name] = forms.CharField()

    def get_incoming_data(self):
        """
        Returns the identify and text for this message, based on the field=
        names passed to __init__().
        """
        return {'identity': self.cleaned_data[self.identity_name],
                'text': self.cleaned_data[self.text_name]}
