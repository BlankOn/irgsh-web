from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext as _
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Q

from settings import FULL_LOGOUT_URL
from settings import LOG_PATH 

from jobs.forms import *
from jobs.models import *
from django.shortcuts import render_to_response
from django.forms.models import inlineformset_factory

import os

def site_logout(request):
    logout(request)
    return render_to_response("logout.html", {
        "full_logout_url": FULL_LOGOUT_URL,
        },
        context_instance=RequestContext(request),
    )

def site_index(request):
    tasks_query = Task.objects.all().order_by('-id')[:5]
    builders = Builder.objects.all().order_by('architecture')

    return render_to_response("index.html", 
        {
            "tasks": tasks_query, 
            "builders": builders, 
        },
        context_instance=RequestContext(request),
    )

def tasks(request):
    tasks_query = Task.objects.all().order_by('-id')
    paginator = Paginator(tasks_query, 30)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        tasks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tasks = paginator.page(paginator.num_pages)

    return render_to_response("tasks.html", 
        {
            "tasks": tasks, 
        },
        context_instance=RequestContext(request),
    )


def task(request, task_id):
    task_query = Task.objects.get(id=task_id)
    assignments_query = TaskAssignment.objects.filter(task=task_query)
    manifest_query = TaskManifest.objects.filter(task=task_query)
    log_query = TaskLog.objects.filter(task=task_query)
    print task_query.state
    if task_query.state == "N" or task_query.state == "A" or task_query.state == "R":
        show_end_time = False
    else:
        show_end_time = True
    return render_to_response("task.html", 
        { 
            "task_id": task_id,
            "task": task_query,
            "show_end_time": show_end_time,
            "manifest": manifest_query,
            "assignments": assignments_query,
            "log": log_query,
        } ,
        context_instance=RequestContext(request),
    )
    
def builder(request, builder_id):
    try:
        builder_query = Builder.objects.get(name=builder_id)
    except:
        return HttpResponseRedirect("/")

    assignments = TaskAssignment.objects.filter(handler=builder_query).order_by('-id')[:5]
       
    return render_to_response("builder.html", 
        { 
            "builder_id": builder_id,
            "builder": builder_query,
            "assignments": assignments,
            "status": builder_query.state(),
        } ,
        context_instance=RequestContext(request),
    )
 
@login_required
def new_job(request):

    TasksInline = inlineformset_factory(Job, Task, extra=5,can_delete=False, formset=TaskInlineFormSet)

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False) 
            formset = TasksInline(request.POST, instance=job)
            if formset.is_valid():
                job.submitter = request.user
                job.save()
                formset.save()

                return render_to_response("new-job.html", {
                    "job_id": job.id
                    },
                    context_instance=RequestContext(request),
                )
        else:
            formset = TasksInline(instance=Job())
    else:
        form = JobForm()
        formset = TasksInline(instance=Job())

    return render_to_response("new-job.html", {
        "form": form,
        "formset": formset,
        },
        context_instance=RequestContext(request),
    )

