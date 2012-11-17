from django.http import HttpResponse

from rapidsms.backends.kannel.forms import KannelForm
from rapidsms.backends.http.views import BaseHttpBackendView


class KannelBackendView(BaseHttpBackendView):
    """Backend view for handling inbound SMSes from Kannel."""

    http_method_names = ['get']
    form_class = KannelForm

    def get(self, *args, **kwargs):
        """Kannel issues a GET instead of a POST, so pass it to post() here."""
        return self.post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(KannelBackendView, self).get_form_kwargs()
        kwargs['data'] = self.request.GET  # passes request.GET to the form
        return kwargs

    def form_valid(self, form):
        super(KannelBackendView, self).form_valid(form)
        # any text in the response will be sent as an SMS, so make that ''
        return HttpResponse('')
