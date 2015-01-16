import copy
import json
import logging
import requests

from rapidsms.backends.base import BackendBase


logger = logging.getLogger(__name__)


class VumiBackend(BackendBase):
    """Outgoing SMS backend for Vumi."""

    def configure(self, sendsms_url, sendsms_params=None, sendsms_user=None,
                  sendsms_pass=None, **kwargs):
        self.sendsms_url = sendsms_url
        self.sendsms_params = sendsms_params or {}
        self.sendsms_user = sendsms_user
        self.sendsms_pass = sendsms_pass

    def prepare_request(self, id_, text, identities, context):
        """Construct outbound data for requests.post."""
        kwargs = {'url': self.sendsms_url,
                  'headers': {'content-type': 'application/json'}}
        payload = copy.copy(self.sendsms_params)
        payload.update({'content': text,
                        'to_addr': identities,
                        'session_event': None,
                        'metadata': {'rapidsms_msg_id': id_}})
        if len(identities) == 1 and 'external_id' in context:
            payload['in_reply_to'] = context['external_id']
        # add endpoint and/or from_addr, if provided
        for key in ['endpoint', 'from_addr']:
            if key in context:
                payload[key] = context[key]
        if self.sendsms_user and self.sendsms_pass:
            kwargs['auth'] = (self.sendsms_user, self.sendsms_pass)
        kwargs['data'] = json.dumps(payload)
        return kwargs

    def send(self, id_, text, identities, context={}):
        logger.debug('Sending message: %s', text)
        kwargs = self.prepare_request(id_, text, identities, context)
        r = requests.post(**kwargs)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
