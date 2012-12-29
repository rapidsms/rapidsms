import copy
import urllib
import urllib2

from rapidsms.backends.base import BackendBase


class KannelBackend(BackendBase):
    """Backend for use with the Kannel SMS Gateway."""

    def configure(self, sendsms_url='http://127.0.0.1:13013/cgi-bin/sendsms',
                  sendsms_params=None, charset=None, coding=None,
                  encode_errors=None, **kwargs):
        self.sendsms_url = sendsms_url
        self.sendsms_params = sendsms_params or {}
        self.charset = charset or 'ascii'
        self.coding = coding or 0
        self.encode_errors = encode_errors or 'ignore'

    def prepare_message(self, text, identities):
        """Prepare URL query string with message context."""
        query = copy.copy(self.sendsms_params)
        query['to'] = ' '.join(identities)
        query['text'] = text.encode(self.charset, self.encode_errors)
        query['coding'] = self.coding
        query['charset'] = self.charset
        return query

    def send(self, text, identities):
        """Open request to Kannel instance."""
        self.info('Sending message: %s' % text)
        url_args = self.prepare_message(text, identities)
        url = '?'.join([self.sendsms_url, urllib.urlencode(url_args)])
        try:
            self.debug('Opening URL: %s' % url)
            response = urllib2.urlopen(url)
        except:
            self.exception('Failed to send message')
            return
        self.info('SENT')
        self.debug('response body: %s' % response.read())
        return True
