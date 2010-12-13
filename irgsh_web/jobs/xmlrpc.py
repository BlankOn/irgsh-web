from django.contrib.auth.decorators import login_required
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

import os

def get_new_tasks():
    retval = []
    tasks = Task.objects.filter(state='N')
    for task in tasks:
        retval.append(task.id)
    return retval 

def get_task_info(task):
    task = Task.objects.get(id=task)
    components = ""
    component_name = ""
    arch_independent = True 
    try:
        manifest = TaskManifest.objects.filter(task=task)
        for entry in manifest:
            if entry.type == "S":
                continue
            if entry.architecture != "all":
                arch_independent = False
                break
    except:
        pass

    try:
        package = Package.objects.get(name=task.package, distribution=task.job.distro)
        component_name = package.component.name
        component = Component.objects.get(name=package.component.name, distribution=task.job.distro)
        components = "%s %s" % (package.component.name, component.others)
    except:
        pass
    log = TaskLog(task=task)
    
    retval = {
        'distribution': task.job.distro.name,
        'debian_url': task.debian_url,
        'debian_vcs': task.debian_vcs,
        'debian_tag': task.debian_tag,
        'orig_url': task.orig_url,
        'state': task.state,
        'debian_copy': task.debian_copy,
        'orig_copy': task.orig_copy,
        'components': components.strip(),
        'component': component_name,
        'arch_independent': arch_independent,
    }

    return retval

def get_assignments_to_upload(handler):
    retval = []
    try:
        handler = Builder.objects.get(name=handler)
        assignments = TaskAssignment.objects.filter(Q(state='W')|Q(state='U'), handler=handler)
        for assignment in assignments:
            retval.append(assignment.id)
    except Exception as e:
        return (-1, str(e)) 
    return (0, retval)

def get_assignments_to_install():
    retval = []
    try:
        assignments = TaskAssignment.objects.filter(state='R')
        for assignment in assignments:
            retval.append(assignment.id)
    except Exception as e:
        return (-1, str(e)) 
    return (0, retval)

def populate_debian_info(task_id, info):
    try:
        task = Task.objects.get(id=task_id)
        try:
            p = Package.objects.get(name=info["source"], distribution=task.job.distro)
        except Exception:
            raise Exception(_("Package %s of distribution %s does not exist in database. Please add it first.") % (info["source"], task.job.distro.name))

        task.package = info["source"]
        task.version = info["version"]
        task.changelog = info["changelog"]

        for package in info["packages"]:
            m = TaskManifest()
            m.task = task
            m.name = package["package"]
            m.architecture = package["architecture"]
            if m.architecture == "source":
                m.type = 'S'
            else:
                m.type = 'B'
            m.save()

        task.save()
        log = TaskLog(task=task)
        log.log(_("Populated debian information"))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")


def set_debian_copy(task_id, url):
    try:
        task = Task.objects.get(id=task_id)
        task.debian_copy = url
        task.save()
        log = TaskLog(task=task)
        log.log(_("Set debian copy to %s" % url))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")


def set_orig_copy(task_id, url):
    try:
        task = Task.objects.get(id=task_id)
        task.orig_copy = url
        task.save()
        log = TaskLog(task=task)
        log.log(_("Set orig copy to %s" % url))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def xstart_running(task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.start_running()
        log = TaskLog(task=task)
        log.log(_("Starting to run"))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def xstart_assigning(task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.start_assigning()
        log = TaskLog(task=task)
        log.log(_("Starting to assign"))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def task_init_failed(task_id, message):
    try:
        task = Task.objects.get(id=task_id)
        task.fail(_("Task initialization failed: %s" % message))
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assign_task(task_id, handler):
    try:
        task_object = Task.objects.get(id=task_id)
        handler_object = Builder.objects.get(name=handler)
        architecture_object = handler_object.architecture
        assignment = TaskAssignment(task=task_object, architecture=architecture_object, handler=handler_object)
        assignment.save()
        log = TaskLog(task=task_object)
        log.log(_("Assigning task %d/%s to %s" % (task_id, str(handler_object.architecture), handler)))
        task_object.start_running()
    except Exception as e:
        return (-1, str(e)) 
    return (0, assignment.id)

def get_assignment_info(assignment):
    try:
        assignment = TaskAssignment.objects.get(id=assignment)
        
        retval = {
            'task': assignment.task.id,
            'architecture': assignment.architecture.architecture,
            'state': assignment.state,
            'dsc': assignment.dsc
        }
        print retval

        return (0, retval)
    except Exception as e:
        return (-1, str(e)) 



def get_assignment_for_builder(handler):
    id = -1
    try:
        handler_object = Builder.objects.get(name=handler)
        architecture_object = handler_object.architecture
        assignments = TaskAssignment.objects.filter(handler=handler_object)
        for assignment in assignments:
            if assignment.new_or_stalled():
                id = assignment.id
                break
    except Exception as e:
        return (-1, str(e)) 
    return (0, id)
        

def assignment_download(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.start_downloading()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_environment(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.start_environment()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_building(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.start_building()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_upload(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.start_uploading()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_complete(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.start_completing()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_fail(id, message):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.fail(message)
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_cancel(id, message):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.cancel(False, message)
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")


def assignment_wait_for_upload(id, dsc):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.wait_for_upload(dsc)
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_wait_for_installing(id):
    try:
        assignment = TaskAssignment.objects.get(id=id)
        assignment.wait_for_installing()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")

def assignment_upload_log(id, filename, data):
    try:
        with open(os.path.join(LOG_PATH, filename), "wb") as handle:
            handle.write(data.data)

        assignment = TaskAssignment.objects.get(id=id)
        assignment.set_log_url(filename)
    except Exception as e:
        raise
        return (-1, str(e)) 
    return (0, "")


def get_unassigned_task(handler):
    id = -1
    try:
        builder = Builder.objects.get(name=handler)
        architecture = builder.architecture
        task = Task.objects.filter(state='A').order_by('-id')[:1]
        if len(task) == 0:
            return (0, -1)

        task[0].start_running()
        assignments = TaskAssignment.objects.filter(task=task[0])
        skip = False
        for assignment in assignments:
            # There is already assignment for this architecuture, skip it
            if assignment.architecture == architecture:
                skip = True
        if skip == False:
            id = task[0].id
    except Exception as e:
        return (-1, str(e)) 
    
    return (0, id)

def builder_ping(id):
    try:
        builder = Builder.objects.get(name=id)
        builder.ping()
    except Exception as e:
        return (-1, str(e)) 
    return (0, "")


#def ()
#    try:
#    except Exception as e:
#        return (-1, str(e)) 
#    return (0, "")



