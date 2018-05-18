import copy
import requests
import logging

from django.urls import reverse
from rapidsms.backends.base import BackendBase


logger = logging.getLogger(__name__)


class KannelBackend(BackendBase):
    """Backend for use with the Kannel SMS Gateway."""

    def configure(self, sendsms_url='http://127.0.0.1:13013/cgi-bin/sendsms',
                  sendsms_params=None, charset=None, coding=None,
                  encode_errors=None, delivery_report_url=None, **kwargs):
        self.sendsms_url = sendsms_url
        self.sendsms_params = sendsms_params or {}
        self.charset = charset or 'ascii'
        self.coding = coding or 0
        self.encode_errors = encode_errors or 'ignore'
        self.delivery_report_url = delivery_report_url

    def prepare_request(self, id_, text, identities, context):
        """Prepare URL query string with message context."""
        kwargs = {'url': self.sendsms_url}
        query = copy.copy(self.sendsms_params)
        query['to'] = ' '.join(identities)
        query['text'] = text.encode(self.charset, self.encode_errors)
        query['coding'] = self.coding
        query['charset'] = self.charset
        if self.delivery_report_url:
            query['dlr-mask'] = 31
            dlr_url_params = ("message_id=%s" % id_,
                              "status=%d",
                              "status_text=%A",
                              "smsc=%i",
                              "sms_id=%I",
                              "date_sent=%t",
                              "identity=%p")
            dlr_url_params = '&'.join(dlr_url_params)
            dlr_url = "%s%s" % (self.delivery_report_url,
                                reverse('kannel-delivery-report'))
            query['dlr-url'] = '?'.join([dlr_url, dlr_url_params])
        kwargs['params'] = query
        return kwargs

    def send(self, id_, text, identities, context=None):
        logger.debug('Sending message: %s', text)
        context = context or {}
        kwargs = self.prepare_request(id_, text, identities, context)
        r = requests.get(**kwargs)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
