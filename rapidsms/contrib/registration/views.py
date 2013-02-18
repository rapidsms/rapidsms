#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import csv
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rapidsms.models import Contact, Connection, Backend
from rapidsms.contrib.registration.tables import ContactTable
from rapidsms.contrib.registration.forms import BulkRegistrationForm, ContactForm


def registration(request):
    return render(request, "registration/dashboard.html", {
        "contacts_table": ContactTable(Contact.objects.all(), request=request)
        })


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


@transaction.commit_on_success
def contact_bulk_add(request):
    bulk_form = BulkRegistrationForm(data=request.POST)

    if request.method == "POST" and "bulk" in request.FILES:
        connections, contacts = [], []
        reader = csv.reader(request.FILES["bulk"], quoting=csv.QUOTE_NONE, skipinitialspace=True)
        for i, row in enumerate(reader, start=1):
            try:
                name, backend_name, identity = row
            except:
                return render(request, 'registration/bulk_form.html', {
                    "bulk_form": bulk_form,
                    "csv_errors": "Could not unpack line " + str(i),
                })
            contact = Contact(name=name)
            contacts.append(contact)
            try:
                backend = Backend.objects.get(name=backend_name)
            except:
                return render(request, 'registration/bulk_form.html', {
                    "bulk_form": bulk_form,
                    "csv_errors": "Could not find Backend.  Line: " + str(i),
                })
            connections.append(Connection(backend=backend, identity=identity,
                                        contact=contact))
        return HttpResponseRedirect(reverse(registration))
    return render(request, 'registration/bulk_form.html', {
        "bulk_form": bulk_form,
        })


def contact_edit(request, pk):
    contact = get_object_or_404(Connection, pk=pk)

    if request.method == "POST":
        if request.POST["submit"] == "Delete Contact":
            contact.delete()
            return HttpResponseRedirect(
                reverse(registration))
        else:
            contact_form = Connection(instance=contact, data=request.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                return HttpResponseRedirect(
                    reverse(registration))
    return render(request, "registration/contact_form.html", {
            "contact": contact
        })
