#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import csv
from io import TextIOWrapper

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django_tables2 import RequestConfig

from rapidsms.conf import settings
from rapidsms.contrib.registration.forms import (
    BulkRegistrationForm,
    ConnectionFormSet,
    ContactForm,
)
from rapidsms.contrib.registration.tables import ContactTable
from rapidsms.models import Backend, Connection, Contact


@login_required
def registration(request):
    contacts_table = ContactTable(
        Contact.objects.all().prefetch_related("connection_set"),
        template_name="django_tables2/bootstrap-tables.html",
    )

    paginate = {"per_page": settings.PAGINATOR_OBJECTS_PER_PAGE}
    RequestConfig(request, paginate=paginate).configure(contacts_table)

    return render(
        request,
        "registration/dashboard.html",
        {
            "contacts_table": contacts_table,
        },
    )


@login_required
def contact(request, pk=None):
    if pk:
        contact = get_object_or_404(Contact, pk=pk)
    else:
        contact = Contact()
    contact_form = ContactForm(instance=contact)
    connection_formset = ConnectionFormSet(instance=contact)
    if request.method == "POST":
        data = {}
        for key in request.POST:
            val = request.POST[key]
            if isinstance(val, str):
                data[key] = val
            else:
                try:
                    data[key] = val[0]
                except (IndexError, TypeError):
                    data[key] = val
        del data
        if pk:
            if "delete_contact" in request.POST:
                contact.delete()
                messages.add_message(request, messages.INFO, "Deleted contact")
                return HttpResponseRedirect(reverse(registration))
            contact_form = ContactForm(request.POST, instance=contact)
        else:
            contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact = contact_form.save(commit=False)
            connection_formset = ConnectionFormSet(request.POST, instance=contact)
            if connection_formset.is_valid():
                contact.save()
                connection_formset.save()
                messages.add_message(request, messages.INFO, "Added contact")
                return HttpResponseRedirect(reverse(registration))
    return render(
        request,
        "registration/contact_form.html",
        {
            "contact": contact,
            "contact_form": contact_form,
            "connection_formset": connection_formset,
        },
    )


@login_required
@transaction.atomic
def contact_bulk_add(request):
    bulk_form = BulkRegistrationForm(request.POST)

    if request.method == "POST" and "bulk" in request.FILES:
        encoding = request.encoding or settings.DEFAULT_CHARSET
        f = TextIOWrapper(request.FILES["bulk"].file, encoding=encoding)
        reader = csv.reader(f, quoting=csv.QUOTE_NONE, skipinitialspace=True)
        count = 0
        for i, row in enumerate(reader, start=1):
            try:
                name, backend_name, identity = row
            except ValueError:
                return render(
                    request,
                    "registration/bulk_form.html",
                    {
                        "bulk_form": bulk_form,
                        "csv_errors": "Could not unpack line " + str(i),
                    },
                )
            contact = Contact.objects.create(name=name)
            try:
                backend = Backend.objects.get(name=backend_name)
            except Backend.DoesNotExist:
                return render(
                    request,
                    "registration/bulk_form.html",
                    {
                        "bulk_form": bulk_form,
                        "csv_errors": "Could not find Backend.  Line: " + str(i),
                    },
                )
            Connection.objects.create(
                backend=backend, identity=identity, contact=contact
            )
            count += 1
        if not count:
            return render(
                request,
                "registration/bulk_form.html",
                {
                    "bulk_form": bulk_form,
                    "csv_errors": "No contacts found in file",
                },
            )
        messages.add_message(request, messages.INFO, "Added %d contacts" % count)
        return HttpResponseRedirect(reverse(registration))
    return render(
        request,
        "registration/bulk_form.html",
        {
            "bulk_form": bulk_form,
        },
    )
