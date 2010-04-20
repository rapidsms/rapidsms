#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rapidsms.utils import render_to_response, paginated
from rapidsms.forms import ContactForm
from rapidsms.models import Contact


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

    def _contact(c):

        # add an 'url' attribute; a link to the edit page, with the same
        # GET parameters as the current view. this hocus-pocus lets us
        # persist the pagination params (page=, per-page=), maintaining
        # the current state of the contacts list (on the left).
        c.url = reverse(registration, args=[c.pk])
        if req.GET: c.url += "?%s" % req.GET.urlencode()

        # add an 'identity' attribute, which is a bit naughty, since
        # a contact can have many of them. but that's an implementation
        # detail, and rarely shows up in practice.
        identities = c.connection_set.values_list('identity', flat=True)
        c.identity = identities[0] if identities else None

        # add an 'is_active' attribute, to highlight the contact if
        # we're currently editing it.
        c.is_active = (contact == c)

        return c

    return render_to_response(req,
        "registration/dashboard.html", {
            "contacts": paginated(req, Contact.objects.all(), wrapper=_contact),
            "contact_form": form,
            "contact": contact
        })
