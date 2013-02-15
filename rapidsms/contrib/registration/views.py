#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rapidsms.forms import ContactForm
from rapidsms.models import Contact
from rapidsms.models import Connection
from rapidsms.models import Backend
from rapidsms.contrib.registration.tables import ContactTable
from rapidsms.contrib.registration.forms import BulkRegistrationForm


def registration(request):
    return render(request, "registration/dashboard.html",
        {"contacts_table": ContactTable(Contact.objects.all(), request=request)},)


def contact_add(request):
    if request.method == 'POST':
        contact_form = ContactForm(data=request.POST)
        if contact_form.is_valid():
            contact_form.save()
            return HttpResponseRedirect(reverse(registration))
    else:
        contact_form = ContactForm()
    return render(request, 'registration/contact_form.html', {
        'contact_form': contact_form,
        })


def contact_bulk_add(request):
    bulk_form = BulkRegistrationForm()
    if "bulk" in request.FILES:
    # TODO use csv module
    #reader = csv.reader(open(req.FILES["bulk"].read(), "rb"))
    #for row in reader:
        for line in request.FILES["bulk"]:
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
        return HttpResponseRedirect(reverse(registration))

    return render(request, 'registration/bulk_form.html', {
        "bulk_form": bulk_form,
        })


@transaction.commit_on_success
def contact_edit(request, pk=None):
    contact = None
    if pk is not None:
        contact = get_object_or_404(Contact, pk=pk)

    if request.method == "POST":
        if request.POST["submit"] == "Delete Contact":
            contact.delete()
            return HttpResponseRedirect(
                reverse(registration))
        else:
            contact_form = ContactForm(
                instance=contact,
                data=request.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                return HttpResponseRedirect(
                    reverse(registration))
    return render(request, "registration/dashboard.html", {
            "contact": contact
        },
    )
