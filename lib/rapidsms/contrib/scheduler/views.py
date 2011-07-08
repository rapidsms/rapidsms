#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from rapidsms.utils.pagination import paginated
from rapidsms.contrib.ajax.utils import call_router

from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.scheduler.forms import ScheduleForm


@login_required
def index(request, template="scheduler/index.html"):
    context = {}
    schedules = EventSchedule.objects.all()
    context['schedules'] = paginated(request, schedules)
    return render_to_response(template, context, context_instance=RequestContext(request))


@login_required
def edit(request, pk, template="scheduler/edit.html"):
    context = {}
    schedule = get_object_or_404(EventSchedule, id=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            context['status'] = _("Schedule '%(name)s' successfully updated" % \
                                {'name':schedule.callback} )
        else:
            context['errors'] = form.errors
    else:
        form = ScheduleForm(instance=schedule)
    context['form'] = form
    context['schedule'] = schedule
    return render_to_response(template, context, context_instance=RequestContext(request))

@require_POST
def test_schedule(request, schedule_pk):
    post = {"schedule_pk": schedule_pk}
    succeed = call_router("scheduler", "run_schedule", **post)
    return HttpResponseRedirect(reverse('scheduler'))
