from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db import models
from datetime import datetime

class Architecture(models.Model):
    architecture = models.CharField(max_length=6, primary_key=True)
    active = models.BooleanField()
    logical = models.BooleanField(default=False)

    def __unicode__(self):
        return self.architecture


class Distribution(models.Model):
    name = models.CharField("Distribution name", max_length=50, primary_key=True)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

class DistributionArchitecture(models.Model):
    name = models.ForeignKey('Distribution')
    architecture = models.ForeignKey(Architecture, limit_choices_to={'logical': False})
    active = models.BooleanField()

    def __unicode__(self):
        return self.name.name

    class Meta:
        unique_together = (("name", "architecture"),)

class Builder(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    location = models.CharField(max_length=100)
    architecture = models.ForeignKey(Architecture, limit_choices_to={'logical': False})
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

class BuilderAdministrator(models.Model):
    handler = models.ForeignKey(Builder)
    administrator = models.ForeignKey(User)
    
    class Meta:
        unique_together = (("handler", "administrator"),)

class Job(models.Model):

    JOB_STATES = (
        ('N', _(u'New')),
        ('S', _(u'Running')),
        ('F', _(u'Failed')),
        ('R', _(u'Restarted')),
        ('C', _(u'Completed')),
        ('X', _(u'Canceled')),
    )

    submitter = models.ForeignKey(User, editable=False)
    submission_time = models.DateTimeField(default=datetime.now,editable=False)
    completion_time = models.DateTimeField(default=datetime.now,editable=False)
    state = models.CharField(max_length=1, choices=JOB_STATES, default=u'N', editable=False)
    distro = models.ForeignKey(Distribution)
    carbon_copy = models.TextField("Cc:", blank=True)

    def __unicode__(self):
        return "%d: %s (%s): %s" % (self.id, self.submitter, self.distro, self.state)

class Task(models.Model):
    TASK_STATES = (
        ('N', _(u'New')),
        ('A', _(u'Waiting for builders')),
        ('R', _(u'Running')),
        ('F', _(u'Failed')),
        ('C', _(u'Completed')),
        ('X', _(u'Canceled')),
    )

    JOB_VCS = (
        ('tarball', _('None (tarball)')),
        ('bzr', _('Bazaar')),
        ('git', _('GIT')),
        ('hg', _('Mercurial')),
    )

    job = models.ForeignKey(Job)
    state = models.CharField(max_length=1, choices=TASK_STATES, default=u'N', editable=False)
    debian_url = models.CharField("Package's URL", max_length=1024)
    debian_vcs = models.CharField("Package's VCS", max_length=10, choices=JOB_VCS)
    debian_tag = models.CharField("Package's Tag", max_length=50, blank=True)
    orig_url = models.CharField("Original source's URL", max_length=1024, blank=True)
    # Copied debian/orig is always a tarball
    debian_copy = models.URLField(max_length=1024, editable=False)
    orig_copy = models.URLField(max_length=1024, editable=False)
    changelog = models.TextField(editable=False)
    package = models.CharField("Package", max_length=150, editable=False, blank=True)
    version = models.CharField("Version", max_length=150, editable=False, blank=True)

    class Meta:
        unique_together = (("job", "state","debian_url", "debian_vcs", "debian_tag", "orig_url"),)

    def start_assigning(self):
        self.state = 'A'
        self.save()

    def start_running(self):
        if self.state != 'A':
            raise Exception("Incorrect state prior to run: %s" % self.state) 

        retval = False
        manifest = TaskManifest.objects.filter(task=self) 
        archs = Architecture.objects.filter(active=True, logical=False)
        total_archs = len(archs)
        assignments = TaskAssignment.objects.filter(task=self)
        total_assignments = len(assignments)
        has_all = 0
        has_any = 0
        for m in manifest:
            if m.type == 'B':
                if m.architecture == "any":
                    has_any = 1
                elif m.architecture == "all":
                    has_all = 1

        can_run = 0
        log = TaskLog(task=self)
        if has_any or has_all:
            if has_any:
                # all builders for all archs has been assigned
                if total_archs == total_assignments:
                    can_run = 1
            else:
                if has_all:
                    # at least one builder build "all" package
                    if total_assignments == 1:
                        can_run = 1
        else:
            # package doesn't contain binary packages
            self.fail(_("Debian manifest doesn't contain any binary package, failing"))

        if can_run:
            self.state = 'R'
            self.save()
            log.log(_("All builders are assigned, running now"))
            return retval

    def fail(self, message):
        self.state = 'F'
        self.save()
        log = TaskLog(task=self)
        log.log(_("Task is failed: %s" % message))

    def cancel(self):
        self.state = 'X'
        self.save()
        log = TaskLog(task=self)
        log.log( _("Task is canceled"))

    def completing(self):
        assignments = TaskAssignment.objects.filter(task=self)
        total_assignments = len(assignments)

        completed_assignments = TaskAssignment.objects.filter(task=self, state='C')
        total_completed_assignments = len(completed_assignments)
        if total_assignments == total_completed_assignments:
            self.state = 'C'
            self.save()
            log = TaskLog(task=self)
            log.log(_("All builders has completed their tasks, completing"))

class TaskLog(models.Model):
    task = models.ForeignKey(Task)
    time = models.DateTimeField(default=datetime.now,editable=False)
    text = models.TextField() 

    def log(self, text):
        self.text = text
        self.save()

class TaskManifest(models.Model):
    MANIFEST_TYPES = (
        ('S', u'Source'),
        ('B', u'Binary'),
    )
    task = models.ForeignKey(Task)
    name = models.CharField(max_length=120) 
    #This field is not related to Architecture model
    architecture = models.CharField(max_length=10)
    type = models.CharField(max_length=1, choices=MANIFEST_TYPES)

    class Meta:
        unique_together = (("task", "name", "architecture", "type"),)
    

class TaskAssignment(models.Model):
    BUILDER_STATES = (
        (u'N', u'New'),
        (u'D', u'Downloading'),
        (u'E', u'Preparing environment'),
        (u'B', u'Building'),
        (u'U', u'Uploading'),
        (u'C', u'Completed'),
        (u'F', u'Failed'),
        (u'X', u'Canceled'),
    )
    task = models.ForeignKey(Task)
    assign_time = models.DateTimeField(default=datetime.now)
    start_time = models.DateTimeField(default=datetime.now)
    completion_time = models.DateTimeField(default=datetime.now)
    architecture = models.ForeignKey(Architecture)
    handler = models.ForeignKey(Builder)
    log_url = models.CharField(max_length=2048) 
    state = models.CharField(max_length=1, choices=BUILDER_STATES, default=u'N')

    tasklog = TaskLog(task = Task(task))
    t=Task(task)

    class Meta:
        unique_together = (("task", "architecture"),)

    def set_log_url(self, url):
        self.log_url = url
        self.save()

    def start_downloading(self):
        self.state = 'D'
        self.start_time = datetime.now()
        self.save()
        self.tasklog.log(_("Builder %s is starting to download" % self.handler))

    def start_environment(self):
        self.state = 'E'
        self.save()
        self.tasklog.log(_("Builder %s is starting to prepare the environment" % self.handler))

    def start_building(self):
        self.state = 'B'
        self.save()
        self.tasklog.log(_("Builder %s is starting to build" % self.handler))

    def start_uploading(self):
        self.state = 'U'
        self.save()
        self.tasklog.log(_("Builder %s is starting to upload" % self.handler))

    def start_completing(self):
        self.state = 'C'
        self.completion_time = datetime.now()
        self.save()
        self.tasklog.log(_("Builder %s is starting to complete task" % self.handler))
        self.task.completing()

    def fail(self):
        self.state = 'F'
        self.completion_time = datetime.now()
        self.save()
        self.task.fail(_("Builder %s fails to complete task" % self.handler))

    def cancel(self):
        self.state = 'X'
        self.completion_time = datetime.now()
        self.save()
        self.tasklog.log(_("Builder %s cancels the task" % self.handler))
        self.task.cancel()

