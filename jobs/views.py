from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.template import RequestContext

from settings import FULL_LOGOUT_URL

from jobs.forms import *
from jobs.models import *
from django.shortcuts import render_to_response
from django.forms.models import inlineformset_factory

def site_logout(request):
    logout(request)
    return render_to_response("logout.html", {
        "full_logout_url": FULL_LOGOUT_URL,
        },
        context_instance=RequestContext(request),
    )

def site_index(request):
    return render_to_response("index.html", 
        context_instance=RequestContext(request),
    )


def task(request, task_id):
    return render_to_response("task.html", 
        { "task_id": task_id} ,
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
