#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rapidsms.utils import render_to_response, paginated
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

    return render_to_response(req,
        "registration/dashboard.html", {
            "contacts_table": ContactTable(Contact.objects.all(), request=req),
            "contact_form": form,
            "contact": contact
        })
