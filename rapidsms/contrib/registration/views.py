#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import csv
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rapidsms.models import Contact, Connection, Backend
from rapidsms.contrib.registration.tables import ContactTable
from rapidsms.contrib.registration.forms import (
    BulkRegistrationForm,
    ContactForm, ConnectionFormSet)


def registration(request):
    contacts_table = ContactTable(
        Contact.objects.all(),
        template="django_tables2/bootstrap-tables.html")
    contacts_table.paginate(page=request.GET.get('page', 1), per_page=10)
    return render(request, "registration/dashboard.html", {
        "contacts_table": contacts_table,
    })


def contact_add(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact = contact_form.save(commit=False)
            connection_formset = ConnectionFormSet(request.POST,
                                                   instance=contact)
            if connection_formset.is_valid():
                contact.save()
                connection_formset.save()
            return HttpResponseRedirect(reverse(registration))
    contact_form = ContactForm()
    connection_formset = ConnectionFormSet(instance=Contact())
    return render(request, 'registration/contact_form.html', {
        'contact_form': contact_form,
        'connection_formset': connection_formset,
    })


@transaction.commit_on_success
def contact_bulk_add(request):
    bulk_form = BulkRegistrationForm(request.POST)

    if request.method == "POST" and "bulk" in request.FILES:
        connections, contacts = [], []
        reader = csv.reader(
            request.FILES["bulk"],
            quoting=csv.QUOTE_NONE,
            skipinitialspace=True
        )
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
    contact = get_object_or_404(Contact, pk=pk)
    contact_form = ContactForm(instance=contact)
    connection_formset = ConnectionFormSet(instance=contact)
    if request.method == "POST":
        if request.POST["submit"] == "Delete Contact":
            contact.delete()
            return HttpResponseRedirect(reverse(registration))
        else:
            contact_form = ContactForm(request.POST, instance=contact)
            if contact_form.is_valid():
                contact = contact_form.save(commit=False)
                connection_formset = ConnectionFormSet(request.POST,
                                                       instance=contact)
                if connection_formset.is_valid():
                    contact.save()
                    connection_formset.save()
                    return HttpResponseRedirect(reverse(registration))
    return render(request, "registration/contact_form.html",
                  {
                      "contact": contact,
                      "contact_form": contact_form,
                      'connection_formset': connection_formset,
                  })
