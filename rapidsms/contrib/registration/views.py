#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from rapidsms.forms import ContactForm
from rapidsms.models import Contact
from rapidsms.models import Connection
from rapidsms.models import Backend
from .tables import ContactTable
from .forms import BulkRegistrationForm


@transaction.commit_on_success
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

        elif "bulk" in req.FILES:
            # TODO use csv module
            #reader = csv.reader(open(req.FILES["bulk"].read(), "rb"))
            #for row in reader:
            for line in req.FILES["bulk"]:
                line_list = line.split(',')
                name = line_list[0].strip()
                backend_name = line_list[1].strip()
                identity = line_list[2].strip()

                contact = Contact(name=name)
                contact.save()
                # TODO deal with errors!
                backend = Backend.objects.get(name=backend_name)

                connection = Connection(backend=backend, identity=identity,
                                        contact=contact)
                connection.save()

            return HttpResponseRedirect(
                reverse(registration))
        else:
            contact_form = ContactForm(
                instance=contact,
                data=req.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                return HttpResponseRedirect(
                    reverse(registration))

    else:
        contact_form = ContactForm(
            instance=contact)
        bulk_form = BulkRegistrationForm()

    return render_to_response(
        "registration/dashboard.html", {
            "contacts_table": ContactTable(Contact.objects.all(), request=req),
            "contact_form": contact_form,
            "bulk_form": bulk_form,
            "contact": contact
        }, context_instance=RequestContext(req)
    )
