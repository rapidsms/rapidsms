import urllib2

from django.utils import simplejson as json

from rapidsms.backends.base import BackendBase


class VumiBackend(BackendBase):
    """ Outgoing SMS backend for Vumi """

    def configure(self, vumi_url, vumi_credentials, **kwargs):
        self.vumi_url = vumi_url
        self.vumi_credentials = vumi_credentials

    def _build_request(self, message):
        """ Construct outbound Request object based on context """
        request = urllib2.Request(self.vumi_url)
        context = {'content': message.text,
                   'to_adr': message.connection.identity}
        request.add_data(json.dumps(context))
        return request

    def send(self, message):
        self.info('Sending message: %s' % message)
        request = self._build_request(message)
        # use HTTP Basic Authentication if credentials are provided
        if self.vumi_credentials:
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.vumi_url,
                                      self.vumi_credentials['username'],
                                      self.vumi_credentials['password'])
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        else:
            handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        try:
            self.debug('Sending: %s' % request.get_full_url())
            response = opener.open(request)
        except Exception, e:
            self.exception(e)
            return
        self.info('SENT')
        self.debug(response)
