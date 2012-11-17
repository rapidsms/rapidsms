from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import FormMixin, ProcessFormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rapidsms.log.mixin import LoggerMixin
from rapidsms.router import receive

from .forms import GenericHttpForm


class BaseHttpBackendView(FormMixin, LoggerMixin, ProcessFormView):

    backend_name = None
    http_method_names = []  # must set in child class

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Wraps the main entry point into the view with the csrf_exempt
        decorator, which most (if not all) clients using this view will not
        know about.
        """
        if 'backend_name' in kwargs:
            self.backend_name = kwargs['backend_name']
        return super(BaseHttpBackendView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        """Always pass backend_name into __init__"""
        kwargs = super(BaseHttpBackendView, self).get_form_kwargs()
        kwargs['backend_name'] = self.backend_name
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        All this view does is processing inbound messages, and they may come
        through get() or post().  Pass HTTP GETs along to post() for
        form validation and subsequent handling by the router.
        """
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If the form validated successfully, passes the message on to the
        router for processing.
        """
        data = form.get_incoming_data()
        receive(**data)
        return HttpResponse('OK')

    def form_invalid(self, form):
        """
        If the form failed to validate, logs the errors and returns a bad
        response to the client.
        """
        errors = dict((k, v[0]) for k, v in form.errors.items())
        self.debug(unicode(errors))
        self.debug(form.non_field_errors())
        for field in form:
            if field.errors:
                self.debug(field.errors)
        return HttpResponseBadRequest('form failed to validate')


class GenericHttpBackendView(BaseHttpBackendView):

    # override these in your base class or URLconf, if needed
    form_class = GenericHttpForm
    http_method_names = ['get', 'post']
    params = None

    def get_form_kwargs(self):
        kwargs = super(GenericHttpBackendView, self).get_form_kwargs()
        # pass the identity and text field names into the form
        if self.params:
            kwargs.update(self.params)
        # if we accept GETs instead of POSTs and this request is a GET,
        # pass the GET parameters into the form
        if 'get' in self.http_method_names and self.request.method == 'GET':
            kwargs['data'] = self.request.GET
        return kwargs
