from django.http import HttpResponse
from django.utils import simplejson as json

from rapidsms.backends.vumi.forms import VumiForm
from rapidsms.backends.http.views import BaseHttpBackendView


class VumiBackendView(BaseHttpBackendView):
    """
    Backend view for handling inbound SMSes from Vumi (http://vumi.org/)
    """

    http_method_names = ['post']
    form_class = VumiForm

    def get_form_kwargs(self):
        """ Load JSON POST data """
        kwargs = super(VumiBackendView, self).get_form_kwargs()
        kwargs['data'] = json.loads(self.request.raw_post_data)
        return kwargs
