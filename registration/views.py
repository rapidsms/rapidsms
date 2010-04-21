#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rapidsms.utils import render_to_response, paginated
from rapidsms.tables import ModelRow
from rapidsms.forms import ContactForm
from rapidsms.models import Contact
from .tables import ContactTable


def registration(req, pk=None):
    contact = None

    if pk is not None:
        contact = get_object_or_404(
            Contact, pk=pk)

    if req.method == "POST":
        if req.POST["submit"] == "Delete Contact":
            contact.delete()
            return HttpResponseRedirect(
                reverse(registration))

        else:
            form = ContactForm(
                instance=contact,
                data=req.POST)

            if form.is_valid():
                contact = form.save()
                return HttpResponseRedirect(
                    reverse(registration))

    else:
        form = ContactForm(
            instance=contact)

    class ContactRow(ModelRow):

        # add an 'url' attribute; a link to the edit page, with the same
        # GET parameters as the current view. this lets us persist the
        # pagination params (page=, per-page=), maintaining the current
        # state of the contacts list (on the left).
        def url(self):
            u = reverse(registration, args=[self.data.pk])
            if req.GET: u += "?%s" % req.GET.urlencode()
            return u

        # add an 'is_active' attr, to highlight the row that we're
        # currently editing (if any) in the form to the right.
        def is_active(self):
            return self.data == contact

    return render_to_response(req,
        "registration/dashboard.html", {
            "contacts": ContactTable(request=req, row_class=ContactRow),
            "contact_form": form,
            "contact": contact
        })
