from django import forms

from rapidsms.router import lookup_connections


class BaseHttpForm(forms.Form):
    """Helper form for validating incoming messages.

    :param backend_name: (Optional) name of the backend
    """

    def __init__(self, *args, **kwargs):
        """Save backend name to form for use later"""
        self.backend_name = kwargs.pop('backend_name')
        super(BaseHttpForm, self).__init__(*args, **kwargs)

    def lookup_connections(self, identities):
        """Simple wrapper to ease connection lookup on child forms."""
        return lookup_connections(self.backend_name, identities)

    def get_incoming_data(self):
        """
        Return a dictionary containing the connection and text
        for this message, based on the field
        names passed to __init__().

        Must be implemented by subclasses.
        """
        raise NotImplementedError()


class GenericHttpForm(BaseHttpForm):

    def __init__(self, *args, **kwargs):
        """
        Saves the identify (phone number) and text field names on self, calls
        super(), and then adds the required fields.
        """
        # defaults to "text" and "identity"
        self.text_name = kwargs.pop('text_name', 'text')
        self.identity_name = kwargs.pop('identity_name', 'identity')
        super(GenericHttpForm, self).__init__(*args, **kwargs)
        self.fields[self.text_name] = forms.CharField()
        self.fields[self.identity_name] = forms.CharField()

    def get_incoming_data(self):
        """
        Returns the connection and text for this message, based on the field
        names passed to __init__().
        """
        identity = self.cleaned_data[self.identity_name]
        connections = self.lookup_connections([identity])
        return {'connection': connections[0],
                'text': self.cleaned_data[self.text_name]}
