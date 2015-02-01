import logging
import pprint

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import CreateView

from rapidsms.backends.kannel.models import DeliveryReport
from rapidsms.backends.kannel.forms import KannelForm
from rapidsms.backends.http.views import BaseHttpBackendView


logger = logging.getLogger(__name__)


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


class DeliveryReportView(CreateView):

    model = DeliveryReport
    fields = ('date_sent', 'message_id', 'identity', 'sms_id', 'smsc', 'status', 'status_text', )
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        """Kannel issues a GET instead of a POST, so pass it to post() here."""
        self.object = None
        return self.post(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DeliveryReportView, self).get_form_kwargs()
        kwargs['data'] = self.request.GET  # passes request.GET to the form
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse('')

    def form_invalid(self, form):
        """
        If the form failed to validate, logs the errors and returns a bad
        response to the client.
        """
        logger.error("%s data:", self.request.method)
        logger.error(pprint.pformat(form.data))
        errors = dict((k, v[0]) for k, v in form.errors.items())
        logger.error(unicode(errors))
        if form.non_field_errors():
            logger.error(form.non_field_errors())
        return HttpResponseBadRequest('form failed to validate')
